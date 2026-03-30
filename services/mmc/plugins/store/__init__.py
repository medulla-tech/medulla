# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from pulse2.version import getVersion, getRevision
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.store.config import StoreConfig
from pulse2.database.store import StoreDatabase
import logging
import urllib.request
import urllib.error
import urllib.parse
import json
import ssl
import os
import subprocess
import shutil

VERSION = "1.0.0"
APIVERSION = "1:0:0"
logger = logging.getLogger()

def getApiVersion():
    return APIVERSION

def activate():
    logger = logging.getLogger()
    config = StoreConfig("store")
    if config.disable:
        logger.warning("Plugin store: disabled by configuration.")
        return False
    if not StoreDatabase().activate(config):
        logger.error("Plugin store: an error occurred during the database initialization")
        return False
    return True

# ============================================
# Store API helper
# ============================================

def _store_api_get(endpoint, params=None):
    """Call the remote store API

    Args:
        endpoint: API endpoint (e.g. '/api/v1/softwares')
        params: dict of query parameters

    Returns:
        dict with API response
    """
    config = StoreConfig("store")
    if not config.store_api_url:
        logger.error("Store API URL not configured in store.ini [store_api] url")
        return None

    base_url = config.store_api_url.rstrip('/')
    url = base_url + endpoint

    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None and v != ''})
        if query:
            url += '?' + query

    headers = {'Accept': 'application/json'}
    if config.store_api_token:
        headers['Authorization'] = f'Bearer {config.store_api_token}'
    req = urllib.request.Request(url, headers=headers, method='GET')

    ssl_context = None
    if config.store_api_skip_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=config.store_api_timeout, context=ssl_context) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        logger.error(f"Store API HTTP error {e.code}: {url}")
        return None
    except Exception as e:
        logger.error(f"Store API error: {e}")
        return None

def _store_api_post(endpoint, data):
    """Call the remote store API with POST

    Args:
        endpoint: API endpoint (e.g. '/api/v1/subscriptions')
        data: dict to send as JSON body

    Returns:
        dict with API response
    """
    config = StoreConfig("store")
    if not config.store_api_url:
        logger.error("Store API URL not configured")
        return None

    base_url = config.store_api_url.rstrip('/')
    url = base_url + endpoint

    body = json.dumps(data).encode('utf-8')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if config.store_api_token:
        headers['Authorization'] = f'Bearer {config.store_api_token}'

    req = urllib.request.Request(url, data=body, headers=headers, method='POST')

    ssl_context = None
    if config.store_api_skip_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=config.store_api_timeout, context=ssl_context) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        logger.error(f"Store API POST HTTP error {e.code}: {url}")
        return None
    except Exception as e:
        logger.error(f"Store API POST error: {e}")
        return None

# ============================================
# Exported XMLRPC functions
# ============================================

def _enrich_with_local_packages(data):
    """Enrich software list with local package existence info from packages API"""
    config = StoreConfig("store")

    # Fetch packages list to match software names to package UUIDs
    packages_map = {}
    if config.store_api_url and config.store_api_token:
        try:
            pkg_list = _fetch_packages_list(config)
            for pkg in pkg_list.get('packages', []):
                pkg_name = pkg.get('software_name', '').lower()
                packages_map[pkg_name] = pkg
        except Exception:
            pass

    packages_dir = os.path.join(config.packages_path, "sharing", "global")
    for item in data:
        # Match with packages.json by name
        soft_name = item.get('name', '').lower().replace(' ', '_')
        pkg = packages_map.get(soft_name) or packages_map.get(item.get('name', '').lower())

        if pkg:
            item['package_uuid'] = pkg.get('uuid')
            package_dir = os.path.join(packages_dir, pkg['uuid'])
            item['package_exists'] = os.path.isdir(package_dir)
            item['deployed_at'] = 'synced' if item['package_exists'] else None
        else:
            item['package_exists'] = False
            item['deployed_at'] = None

    return data

def get_all_software(active_only=True, start=0, limit=0, sort="popular"):
    """Get all software from remote store API

    Returns:
        dict with 'total' count and 'data' list
    """
    result = _store_api_get('/api/v1/softwares')
    if not result or not result.get('success'):
        return {'total': 0, 'data': []}

    data = _enrich_with_local_packages(result.get('data', []))
    return {'total': result.get('count', len(data)), 'data': data}

def get_software_by_id(software_id):
    """Get software by ID from remote store API"""
    result = _store_api_get('/api/v1/softwares', {'id': software_id})
    if not result or not result.get('success'):
        return None
    return result.get('data')

def get_filters():
    """Get distinct values for filters from remote store API

    Normalizes API response to simple string lists expected by the frontend.
    """
    result = _store_api_get('/api/v1/filters')
    if not result or not result.get('success'):
        return {'os': [], 'vendor': [], 'track': [], 'arch': []}

    data = result.get('data', {})
    filters = {}
    # API returns objects {value, label} for os/tracks/archs, extract just values
    filters['os'] = [item['value'] if isinstance(item, dict) else item for item in data.get('os', [])]
    filters['vendor'] = [item if isinstance(item, str) else str(item) for item in data.get('vendors', data.get('vendor', []))]
    filters['track'] = [item['value'] if isinstance(item, dict) else item for item in data.get('tracks', data.get('track', []))]
    filters['arch'] = [item['value'] if isinstance(item, dict) else item for item in data.get('archs', data.get('arch', []))]
    return filters

def search_software(filters=None, start=0, limit=0, sort="popular"):
    """Search software from remote store API

    Returns:
        dict with 'total' count and 'data' list
    """
    config = StoreConfig("store")
    params = {}
    if filters:
        if filters.get('search'):
            params['search'] = filters['search']
        if filters.get('os'):
            params['os'] = filters['os']
        if filters.get('vendor'):
            params['vendor'] = filters['vendor']
        if filters.get('track'):
            params['track'] = filters['track']

    result = _store_api_get('/api/v1/softwares', params)
    if not result or not result.get('success'):
        return {'total': 0, 'data': []}

    data = _enrich_with_local_packages(result.get('data', []))

    return {'total': result.get('count', len(data)), 'data': data}

def get_pending_requests():
    """Get pending software requests - not available via API"""
    return []

def get_store_stats():
    """Get store statistics from remote store API"""
    result = _store_api_get('/api/v1/softwares')
    if not result or not result.get('success'):
        return {'total_software': 0, 'active_software': 0, 'total_downloads': 0, 'pending_requests': 0}
    return {
        'total_software': result.get('count', 0),
        'active_software': result.get('count', 0),
        'total_downloads': 0,
        'pending_requests': 0
    }

# ============================================
# XMLRPC functions for subscriptions
# ============================================

def get_client_uuid():
    """Return the client UUID configured in store.ini"""
    config = StoreConfig("store")
    return config.client_uuid or ""

def get_client_info():
    """Return current client info from store API"""
    result = _store_api_get('/api/v1/client')
    if not result or not result.get('success'):
        return None
    return result.get('data')

def get_client_subscriptions():
    """Return software IDs the client is subscribed to from store API"""
    result = _store_api_get('/api/v1/subscriptions')
    if not result or not result.get('success'):
        return []
    return result.get('data', [])

def save_subscriptions(software_ids):
    """Save client subscriptions via store API"""
    config = StoreConfig("store")
    if not config.store_api_token:
        return {'success': False, 'error': 'API token not configured'}

    result = _store_api_post('/api/v1/subscriptions', {'software_ids': software_ids})
    if not result:
        return {'success': False, 'error': 'Failed to contact store API'}

    if not result.get('success'):
        return result

    # Sync packages if store_api is configured
    if config.store_api_url and config.store_api_token:
        logger.info("Syncing packages from store...")
        try:
            sync_result = sync_packages()
            result['sync'] = sync_result
            if not sync_result.get('success'):
                logger.warning(f"Package sync had errors: {sync_result.get('errors')}")
        except Exception as e:
            logger.error(f"Package sync failed: {e}")
            result['sync'] = {'success': False, 'error': str(e)}

    return result

def get_subscribers_for_software(software_id):
    """Return clients subscribed to a software - not available via client API"""
    return []

# ============================================
# Package sync functions (PULL mode)
# ============================================

def sync_packages():
    """
    Sync packages based on current subscriptions.
    Fetches the catalog from store API, the packages list from packages API,
    and downloads packages for subscribed software.

    Returns:
        dict with success status, synced count, and any errors
    """
    config = StoreConfig("store")
    logger = logging.getLogger()

    # Validate configuration
    if not config.store_api_url:
        return {'success': False, 'error': 'store_api url not configured in store.ini'}
    if not config.store_api_token:
        return {'success': False, 'error': 'store_api api_token not configured in store.ini'}

    # 1. Get subscribed software IDs from store API
    subscribed_ids = get_client_subscriptions()
    if not subscribed_ids:
        logger.info("No subscriptions found, nothing to sync")
        return {'success': True, 'synced': 0, 'message': 'No subscriptions'}

    # 2. Get catalog to map software_id -> software_name
    catalog = _store_api_get('/api/v1/softwares')
    if not catalog or not catalog.get('success'):
        return {'success': False, 'error': 'Failed to fetch catalog'}

    # Build name lookup: id -> name (lowercase, normalized)
    subscribed_names = set()
    for soft in catalog.get('data', []):
        if soft.get('id') in subscribed_ids:
            # Normalize name for matching with packages.json software_name
            name = soft.get('name', '').lower().replace(' ', '_')
            subscribed_names.add(name)
            # Also try the raw name
            subscribed_names.add(soft.get('name', '').lower())

    logger.info(f"Subscribed to {len(subscribed_ids)} software, matched names: {subscribed_names}")

    # 3. Fetch available packages from packages API
    try:
        available_packages = _fetch_packages_list(config)
    except Exception as e:
        logger.error(f"Failed to fetch packages list: {e}")
        return {'success': False, 'error': f'Failed to fetch packages list: {e}'}

    # 4. Filter packages matching subscribed software
    packages_to_sync = []
    for pkg in available_packages.get('packages', []):
        pkg_name = pkg.get('software_name', '').lower()
        if pkg_name in subscribed_names:
            packages_to_sync.append(pkg)

    if not packages_to_sync:
        logger.info("No packages available for subscribed software")
        return {'success': True, 'synced': 0, 'message': 'No packages available'}

    logger.info(f"Syncing {len(packages_to_sync)} packages")

    synced = 0
    errors = []
    packages_dir = config.packages_path
    synced_uuids = set()

    # 5. Download each package
    for pkg in packages_to_sync:
        uuid = pkg['uuid']
        name = pkg.get('name', pkg.get('software_name', 'unknown'))
        local_path = os.path.join(packages_dir, "sharing", "global", uuid)
        synced_uuids.add(uuid)

        try:
            result = _download_package(config, pkg, local_path)
            if result['success']:
                conf_exists = os.path.exists(os.path.join(local_path, 'conf.json'))
                xmppdeploy_exists = os.path.exists(os.path.join(local_path, 'xmppdeploy.json'))

                if conf_exists and xmppdeploy_exists:
                    synced += 1
                    logger.info(f"Synced package {uuid} ({name})")
                else:
                    errors.append(f"{uuid}: Package files missing after download")
            else:
                errors.append(f"{uuid}: {result.get('error', 'Unknown error')}")
        except Exception as e:
            errors.append(f"{uuid}: {e}")
            logger.error(f"Failed to sync package {uuid}: {e}")

    # 6. Cleanup unsubscribed packages
    removed = 0
    removed_packages = []
    try:
        removed, removed_packages = _cleanup_unsubscribed_packages(config, synced_uuids)
        if removed > 0:
            logger.info(f"Cleaned up {removed} unsubscribed packages: {removed_packages}")
    except Exception as e:
        logger.error(f"Failed to cleanup unsubscribed packages: {e}")
        errors.append(f"Cleanup failed: {e}")

    # 7. Regenerate Medulla package database
    if synced > 0 or removed > 0:
        try:
            _regenerate_packages(config)
            logger.info("Package database regenerated successfully")
        except Exception as e:
            logger.error(f"Failed to regenerate package database: {e}")
            errors.append(f"Regeneration failed: {e}")

    return {
        'success': len(errors) == 0,
        'synced': synced,
        'removed': removed,
        'removed_packages': removed_packages if removed_packages else None,
        'total_subscribed': len(packages_to_sync),
        'errors': errors if errors else None
    }

def _fetch_packages_list(config):
    """Fetch the packages list from packages API"""
    url = config.store_api_url.rstrip('/') + '/api/v1/packages'

    headers = {'Accept': 'application/json'}
    if config.store_api_token:
        headers['Authorization'] = f'Bearer {config.store_api_token}'

    req = urllib.request.Request(url, headers=headers, method='GET')

    ssl_context = None
    if config.store_api_skip_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, timeout=config.store_api_timeout, context=ssl_context) as response:
        return json.loads(response.read().decode('utf-8'))

def _download_package(config, remote_pkg, local_path):
    """Download all files for a package from packages API"""
    logger = logging.getLogger()

    # Create local directory
    os.makedirs(local_path, exist_ok=True)

    files = remote_pkg.get('files', [])
    path = remote_pkg.get('path', '')

    if not files:
        return {'success': False, 'error': 'No files in package'}

    base_url = config.store_api_url.rstrip('/')

    ssl_context = None
    if config.store_api_skip_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    for filename in files:
        file_url = f"{base_url}/api/v1/packages/download?path={urllib.parse.quote(path + '/' + filename)}"
        local_file = os.path.join(local_path, filename)

        # Skip if file already exists and has content
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            # For conf.json and xmppdeploy.json, always re-download (might have changed)
            if filename not in ('conf.json', 'xmppdeploy.json'):
                logger.debug(f"Skipping {filename}, already exists")
                continue

        logger.debug(f"Downloading {filename} from {file_url}")

        headers = {}
        if config.store_api_token:
            headers['Authorization'] = f'Bearer {config.store_api_token}'
        req = urllib.request.Request(file_url, headers=headers, method='GET')

        try:
            with urllib.request.urlopen(req, timeout=config.store_api_timeout, context=ssl_context) as response:
                with open(local_file, 'wb') as f:
                    shutil.copyfileobj(response, f)
        except urllib.error.HTTPError as e:
            return {'success': False, 'error': f'Failed to download {filename}: HTTP {e.code}'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to download {filename}: {e}'}

    return {'success': True}

def _cleanup_unsubscribed_packages(config, subscribed_uuids):
    """
    Remove packages that are not in the subscribed list.

    Args:
        config: StoreConfig instance
        subscribed_uuids: set of package UUIDs we're subscribed to

    Returns:
        tuple: (count of removed packages, list of removed UUIDs)
    """
    import re
    logger = logging.getLogger()

    packages_dir = os.path.join(config.packages_path, "sharing", "global")

    if not os.path.isdir(packages_dir):
        return 0, []

    # UUID pattern
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

    removed = 0
    removed_packages = []

    for entry in os.listdir(packages_dir):
        entry_path = os.path.join(packages_dir, entry)

        # Only process UUID-named directories
        if not os.path.isdir(entry_path):
            continue
        if not uuid_pattern.match(entry):
            continue

        # Skip if subscribed
        if entry in subscribed_uuids:
            continue

        # Remove unsubscribed package
        try:
            shutil.rmtree(entry_path)
            removed += 1
            removed_packages.append(entry)
            logger.info(f"Removed unsubscribed package: {entry}")
        except Exception as e:
            logger.error(f"Failed to remove package {entry}: {e}")

    return removed, removed_packages

def _regenerate_packages(config):
    """Run pulse2-generation_package.py to register packages in Medulla"""
    import configparser

    script = config.generate_package_script

    if not os.path.exists(script):
        raise Exception(f"Generate package script not found: {script}")

    # Read pkgs database password from config
    pkgs_config = configparser.ConfigParser()
    pkgs_config.read(['/etc/mmc/plugins/pkgs.ini', '/etc/mmc/plugins/pkgs.ini.local'])

    db_user = pkgs_config.get('database', 'dbuser', fallback='mmc')
    db_pass = pkgs_config.get('database', 'dbpasswd', fallback='mmc')
    db_host = pkgs_config.get('database', 'dbhost', fallback='localhost')
    db_port = pkgs_config.get('database', 'dbport', fallback='3306')

    # Run the script with appropriate flags and credentials
    # -r: report, -l: linkcreate, -g: regeneratetable
    # -u: user, -p: password, -H: host, -P: port
    cmd = [script, '-r', '-l', '-g', '-u', db_user, '-p', db_pass, '-H', db_host, '-P', db_port]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        raise Exception(f"Script failed with code {result.returncode}: {result.stderr}")

def create_software_request(software_name, os, requester_name, requester_email, message=""):
    """Create a new software request via store API"""
    # TODO: implement via store API when endpoint is available
    result = _store_api_post('/api/v1/requests', {
        'software_name': software_name,
        'os': os or '',
        'requester_name': requester_name,
        'requester_email': requester_email,
        'message': message or ''
    })
    if not result:
        result = {'success': False, 'error': 'Failed to contact store API'}

    if not result.get('success'):
        return result

    # 2. Call AI webhook if enabled
    config = StoreConfig("store")
    if config.ai_webhook_url:
        try:
            webhook_data = {
                'request_id': result.get('id'),
                'software_name': software_name,
                'os': os or '',
                'requester_name': requester_name,
                'requester_email': requester_email,
                'message': message or ''
            }

            req = urllib.request.Request(
                config.ai_webhook_url,
                data=json.dumps(webhook_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # Create SSL context (optionally skip verification for self-signed certs)
            ssl_context = None
            if config.store_api_skip_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                logging.getLogger().info(f"AI webhook called successfully for request {result.get('id')}")
        except urllib.error.URLError as e:
            logging.getLogger().warning(f"AI webhook call failed: {e}")
        except Exception as e:
            logging.getLogger().warning(f"AI webhook error: {e}")

    return result
