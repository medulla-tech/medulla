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
import json
import ssl

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
        logger.warning("Plugin store: an error occurred during the database initialization")
        return False
    return True

# ============================================
# Exported XMLRPC functions
# ============================================

def get_all_software(active_only=True, start=0, limit=0, sort="popular"):
    """Get all software with local package existence check

    Args:
        active_only: Only return active software
        start: Offset for pagination (0 = from beginning)
        limit: Max number of results (0 = no limit)
        sort: Sort order - 'popular', 'name', or 'recent'

    Returns:
        dict with 'total' count and 'data' list
    """
    config = StoreConfig("store")
    return StoreDatabase().get_all_software(active_only, config.packages_path, start, limit, sort)

def get_software_by_id(software_id):
    """Get software by ID"""
    return StoreDatabase().get_software_by_id(int(software_id))

def get_filters():
    """Get distinct values for filters"""
    return StoreDatabase().get_filters()

def search_software(filters=None, start=0, limit=0, sort="popular"):
    """Search software with filters and local package existence check

    Args:
        filters: dict with search, os, vendor, track, arch keys
        start: Offset for pagination (0 = from beginning)
        limit: Max number of results (0 = no limit)
        sort: Sort order - 'popular', 'name', or 'recent'

    Returns:
        dict with 'total' count and 'data' list
    """
    config = StoreConfig("store")
    return StoreDatabase().search_software(filters, config.packages_path, start, limit, sort)

def get_pending_requests():
    """Get pending software requests"""
    return StoreDatabase().get_pending_requests()

def get_store_stats():
    """Get store statistics"""
    return StoreDatabase().get_store_stats()

# ============================================
# XMLRPC functions for subscriptions
# ============================================

def get_client_uuid():
    """Return the client UUID configured in store.ini"""
    config = StoreConfig("store")
    return config.client_uuid or ""

def get_client_info():
    """Return current client info"""
    config = StoreConfig("store")
    if not config.client_uuid:
        return None
    return StoreDatabase().get_client_by_uuid(config.client_uuid)

def get_client_subscriptions():
    """Return software IDs the client is subscribed to"""
    config = StoreConfig("store")
    if not config.client_uuid:
        return []
    return StoreDatabase().get_client_subscriptions(config.client_uuid)

def save_subscriptions(software_ids):
    """Save client subscriptions and trigger sync webhook if configured"""
    config = StoreConfig("store")
    if not config.client_uuid:
        return {'success': False, 'error': 'Client UUID not configured'}

    # 1. Save subscriptions to database
    result = StoreDatabase().save_subscriptions(config.client_uuid, software_ids)

    if not result.get('success'):
        return result

    # 2. Call Kestra sync webhook if enabled
    if config.kestra_enabled and config.kestra_sync_webhook_url:
        try:
            webhook_data = {
                'client_uuid': config.client_uuid,
                'software_ids': software_ids,
                'count': len(software_ids)
            }

            req = urllib.request.Request(
                config.kestra_sync_webhook_url,
                data=json.dumps(webhook_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # Create SSL context (optionally skip verification for self-signed certs)
            ssl_context = None
            if config.kestra_skip_ssl_verify:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                logging.getLogger().info(f"Kestra sync webhook called successfully for client {config.client_uuid}")
        except urllib.error.URLError as e:
            logging.getLogger().warning(f"Kestra sync webhook call failed: {e}")
        except Exception as e:
            logging.getLogger().warning(f"Kestra sync webhook error: {e}")

    return result

def get_subscribers_for_software(software_id):
    """Return clients subscribed to a software (for Kestra)"""
    return StoreDatabase().get_subscribers_for_software(int(software_id))

def create_software_request(software_name, os, requester_name, requester_email, message=""):
    """Create a new software request and trigger Kestra webhook if configured"""
    # 1. Insert into database
    result = StoreDatabase().create_software_request(software_name, os, requester_name, requester_email, message)

    if not result.get('success'):
        return result

    # 2. Call Kestra AI webhook if enabled
    config = StoreConfig("store")
    if config.kestra_enabled and config.kestra_ai_webhook_url:
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
                config.kestra_ai_webhook_url,
                data=json.dumps(webhook_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            # Create SSL context (optionally skip verification for self-signed certs)
            ssl_context = None
            if config.kestra_skip_ssl_verify:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                logging.getLogger().info(f"Kestra AI webhook called successfully for request {result.get('id')}")
        except urllib.error.URLError as e:
            logging.getLogger().warning(f"Kestra webhook call failed: {e}")
        except Exception as e:
            logging.getLogger().warning(f"Kestra webhook error: {e}")

    return result
