# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision  # pyflakes.ignore
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.security.config import SecurityConfig
from pulse2.database.security import SecurityDatabase
from pulse2.managers.location import ComputerLocationManager
import logging

VERSION = "1.0.0"
APIVERSION = "1:0:0"
logger = logging.getLogger()


def getApiVersion():
    return APIVERSION


def activate():
    config = SecurityConfig("security")
    if config.disable:
        logger.warning("Plugin security: disabled by configuration.")
        return False
    if not SecurityDatabase().activate(config):
        logger.error("Plugin security: an error occurred during the database initialization")
        return False
    logger.info("Plugin security: activated successfully")
    return True


def _ids(location):
    """'UUID1,UUID2' (or a list) -> [1, 2]; None when empty (no filter)."""
    items = location.split(',') if isinstance(location, str) else location or []
    ids = []
    for item in items:
        item = str(item).strip()
        item = item[4:] if item.startswith('UUID') else item
        if item.isdigit():
            ids.append(int(item))
    return ids or None


def _bool(value):
    return value in (True, 1, '1', 'true', 'True', 'on')


def _filters():
    return SecurityConfig("security").filters()


def get_contract_status():
    """Effective access status: {'configured', 'has_access', 'reason'}.

    The .ini is read on each call so that a new AES key is used without restarting mmc-agent.
    """
    import configparser
    from mmc.plugins.security.scanner import CVECentralClient

    parser = configparser.ConfigParser()
    parser.read(['/etc/mmc/plugins/security.ini', '/etc/mmc/plugins/security.ini.local'])

    if not parser.has_section('cve_central'):
        return {'configured': False, 'has_access': False, 'reason': 'not_configured'}

    url = parser.get('cve_central', 'url', fallback='').strip()
    server_id = parser.get('cve_central', 'server_id', fallback='').strip()
    aes_key = parser.get('cve_central', 'keyAES32', fallback='').strip()

    if not all([url, server_id, aes_key]):
        return {'configured': False, 'has_access': False, 'reason': 'not_configured'}
    if len(aes_key.encode('utf-8')) != 32:
        logger.warning("[cve_central] keyAES32 must be 32 characters")
        return {'configured': True, 'has_access': False, 'reason': 'contract_required'}

    try:
        client = CVECentralClient(url, server_id, aes_key,
                                  parser.getboolean('cve_central', 'ssl_verify', fallback=True))
        runtime_status = client.get_access_status()
        reason = runtime_status.get('reason', 'access_denied')
        # A credential issue means a missing contract, not a transient outage.
        if reason in ('unknown_server', 'decrypt_failed', 'server_mismatch'):
            reason = 'contract_required'
        return {
            'configured': True,
            'has_access': bool(runtime_status.get('authorized')),
            'reason': reason
        }
    except Exception as e:
        logger.warning(f"Unable to evaluate contract status: {e}")
        return {'configured': True, 'has_access': False, 'reason': 'service_unreachable'}


def get_policies():
    """Effective display and exclusion policies."""
    cfg = SecurityConfig("security")
    return {'display': cfg.get_display_policies(), 'exclusions': cfg.get_exclusion_policies()}


def get_software_cves(software_name, software_version, start=0, limit=50, filter_str='', severity=None):
    """CVEs of a software version (no machine listed: not restricted by entity)."""
    return SecurityDatabase().get_software_cves(
        software_name, software_version, int(start), int(limit), filter_str, severity or None,
        policy=_filters())


class ContextMaker(ContextMakerI):
    def getContext(self):
        ctx = SecurityContext()
        ctx.userid = self.userid
        return ctx


class RpcProxy(RpcProxyI):
    """Reads restricted to the entities of the logged user (session), whatever the PHP sends."""

    def _allowed(self):
        """Entity ids visible to the session user, None when unrestricted.
        Kept in the proxy: a module function would be callable over XML-RPC for any login."""
        ctx = self.currentContext or SecurityContext()
        if not hasattr(ctx, 'entity_ids'):
            manager = ComputerLocationManager()
            if self.userid == 'root' or manager.main not in manager.components:
                ctx.entity_ids = None
            else:
                try:
                    ctx.entity_ids = _ids([loc['uuid'] for loc in manager.getUserLocations(self.userid) or []]) or []
                except Exception as e:
                    logger.error(f"Security: cannot get the entities of {self.userid}: {e}")
                    ctx.entity_ids = []
        return ctx.entity_ids

    def _entities(self, location=''):
        """Requested entities within the allowed ones; None = all."""
        allowed, requested = self._allowed(), _ids(location)
        if allowed is None or requested is None:
            return requested if allowed is None else allowed
        return [e for e in requested if e in allowed]

    def _login(self):
        return None if self.userid == 'root' else self.userid

    def get_dashboard_summary(self, location='', platform='', exploited_only=False):
        return SecurityDatabase().get_dashboard_summary(
            self._entities(location), _filters(), platform, _bool(exploited_only))

    def get_cves(self, start=0, limit=50, filter_str='', severity=None, location='',
                 sort_by='cvss_score', sort_order='desc', platform='', exploited_only=False):
        """sort_by/sort_order are ignored: exploited CVEs first, then CVSS."""
        return SecurityDatabase().get_cves(
            int(start), int(limit), filter_str, severity or None, self._entities(location), _filters(),
            platform, _bool(exploited_only))

    def get_cve_details(self, cve_id, location=''):
        return SecurityDatabase().get_cve_details(cve_id, self._entities(location), _filters())

    def get_machines_summary(self, start=0, limit=50, filter_str='', location='', platform='',
                             exploited_only=False, group_id=''):
        """group_id: only the machines of this group, if visible to the logged user."""
        return SecurityDatabase().get_machines_summary(
            int(start), int(limit), filter_str, self._entities(location), _filters(), platform,
            _bool(exploited_only), int(group_id) if str(group_id).isdigit() else None, self._login())

    def get_machine_cves(self, id_glpi, start=0, limit=50, filter_str='', severity=None):
        return SecurityDatabase().get_machine_cves(
            int(id_glpi), int(start), int(limit), filter_str, severity or None, self._allowed(), _filters())

    def get_machine_softwares_summary(self, id_glpi, start=0, limit=50, filter_str='', category_filter=''):
        return SecurityDatabase().get_machine_softwares_summary(
            int(id_glpi), int(start), int(limit), filter_str, category_filter, self._allowed(), _filters())

    def get_softwares_summary(self, start=0, limit=50, filter_str='', location='', category_filter='',
                              platform='', exploited_only=False):
        return SecurityDatabase().get_softwares_summary(
            int(start), int(limit), filter_str, self._entities(location), category_filter, _filters(),
            platform, _bool(exploited_only))

    def get_entities_summary(self, start=0, limit=50, filter_str='', user_entities='', platform='',
                             exploited_only=False):
        """user_entities: optional entity filter (UUIDs), restricted to the allowed ones."""
        return SecurityDatabase().get_entities_summary(
            int(start), int(limit), filter_str, self._entities(user_entities), _filters(), platform,
            _bool(exploited_only))

    def get_groups_summary(self, start=0, limit=50, filter_str='', user_login='', platform='',
                           exploited_only=False):
        """user_login is ignored: the groups are the ones of the logged user."""
        return SecurityDatabase().get_groups_summary(
            int(start), int(limit), filter_str, self._login(), self._allowed(), _filters(), platform,
            _bool(exploited_only))

    def get_groups_list(self):
        """[{id, name}] of the groups visible to the logged user, for a selector."""
        return SecurityDatabase().get_groups_list(self._login(), _filters())

    def get_group_machines(self, group_id, start=0, limit=50, filter_str=''):
        return SecurityDatabase().get_group_machines(
            int(group_id), int(start), int(limit), filter_str, self._login(), self._allowed(), _filters())

    def get_machines_by_severity(self, severity, location=''):
        """UUID and hostname of the machines affected by a CVE of this severity."""
        return SecurityDatabase().get_machines_by_severity(severity, self._entities(location), _filters())

    def get_machines_for_vulnerable_software(self, software_name, software_version, location='',
                                             start=0, limit=100, filter_str=''):
        return SecurityDatabase().get_machines_for_vulnerable_software(
            software_name, software_version, self._entities(location), int(start), int(limit), filter_str)

    def scan_machine(self, id_glpi):
        """Scan a machine in background; scan id, 0 when the machine is out of scope."""
        from threading import Thread
        from mmc.plugins.security.scanner import run_cve_scan

        id_glpi = int(id_glpi)
        hostname = SecurityDatabase.machine_name(id_glpi, self._allowed())
        if hostname is None:
            logger.warning(f"Security: {self.userid} cannot scan machine id_glpi={id_glpi}")
            return 0
        scan_id = SecurityDatabase().create_scan()
        Thread(target=run_cve_scan, args=(scan_id, None, None, id_glpi, hostname), daemon=True).start()
        logger.info(f"Started CVE scan for machine '{hostname}' (id_glpi={id_glpi}) with scan ID: {scan_id}")
        return scan_id

    def set_policies_json(self, policies_json, user=None):
        """Store policies given as a JSON string (nested arrays break PHP XML-RPC); user is ignored."""
        import json
        try:
            return SecurityDatabase().set_policies_bulk(json.loads(policies_json), self.userid)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in set_policies_json: {e}")
            return False

    def reset_display_policies(self, user=None):
        """Reset the display policies to their defaults, exclusions kept; user is ignored."""
        return SecurityDatabase().reset_display_policies(user=self.userid)
