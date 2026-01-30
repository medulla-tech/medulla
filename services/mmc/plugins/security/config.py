# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.security.config import SecurityDatabaseConfig
import logging

logger = logging.getLogger()


class SecurityConfig(PluginConfig, SecurityDatabaseConfig):
    """
    Security plugin configuration.

    Configuration sources:
    - [main] and [cve_central]: read from .ini files only (security reasons)
    - [display] and [exclusions]: read from database only (policies table)

    Note: Display and exclusion policies are managed via the UI and stored in DB.
    The .ini file should NOT contain [display] or [exclusions] sections.
    Default values are defined in schema-001.sql and inserted at installation.
    """

    # Valid severity levels in order
    SEVERITY_LEVELS = ['None', 'Low', 'Medium', 'High', 'Critical']

    def __init__(self, name='security', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            SecurityDatabaseConfig.__init__(self)
            self.initdone = True
            self._db_policies_loaded = False

    def _ensure_db_policies_loaded(self):
        """Lazy load DB policies on first access."""
        if not self._db_policies_loaded:
            self._load_db_policies()
            self._db_policies_loaded = True

    def reload_policies(self):
        """Force reload policies from database.

        Call this after modifying policies to ensure the config
        reflects the latest values.
        """
        self._db_policies_loaded = False
        self._load_db_policies()
        self._db_policies_loaded = True

    # Attributes that trigger lazy loading from DB
    _POLICY_ATTRS = {
        'display_min_cvss', 'display_min_severity', 'display_show_patched',
        'display_max_age_days', 'display_min_published_year',
        'excluded_vendors', 'excluded_names', 'excluded_cve_ids',
        'excluded_machines_ids', 'excluded_groups_ids'
    }

    def setDefault(self):
        PluginConfig.setDefault(self)
        # Logging
        self.log_level = 'INFO'
        # CVE Central connection
        self.cve_central_url = ''
        self.cve_central_server_id = ''
        self.cve_central_keyAES32 = ''
        self.use_websocket = True

    def __getattr__(self, name):
        """Lazy load policies from DB on first access to policy attributes."""
        if name in self._POLICY_ATTRS:
            self._ensure_db_policies_loaded()
            # After loading, the attribute should exist with _ prefix
            return getattr(self, f'_{name}')
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def readConf(self):
        PluginConfig.readConf(self)
        SecurityDatabaseConfig.setup(self, self.conffile)

        # [main] section - from .ini file only
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.safe_get("main", "tempdir", "/tmp/mmc-security")
        self.log_level = self.safe_get("main", "log_level", "INFO").upper()

        # [cve_central] section - from .ini file only
        if self.has_section("cve_central"):
            self.cve_central_url = self.safe_get("cve_central", "url", "")
            self.cve_central_server_id = self.safe_get("cve_central", "server_id", "")
            self.cve_central_keyAES32 = self.safe_get("cve_central", "keyAES32", "")
            use_ws = self.safe_get("cve_central", "use_websocket", "true").lower()
            self.use_websocket = use_ws in ('true', '1', 'yes', 'on')

        # NOTE: [display] and [exclusions] are NOT read from .ini
        # They are loaded from database via _load_db_policies()

    def safe_get(self, section, option, default=''):
        """Get config value with fallback to default"""
        try:
            return self.get(section, option)
        except:
            return default

    def _parse_list(self, val, transform=None):
        """Parse a value into a list, handling string/list/None inputs."""
        if isinstance(val, list):
            items = val
        elif isinstance(val, str) and val:
            items = [v.strip() for v in val.split(',') if v.strip()]
        else:
            return []
        return [transform(v) for v in items] if transform else items

    def _parse_int_list(self, val):
        """Parse a value into a list of integers."""
        if isinstance(val, list):
            return [int(v) for v in val if str(v).isdigit()]
        elif isinstance(val, str) and val:
            return [int(v.strip()) for v in val.split(',') if v.strip().isdigit()]
        return []

    def _load_db_policies(self):
        """Load policies from database."""
        try:
            from pulse2.database.security import SecurityDatabase
            db = SecurityDatabase()
            if not db.is_activated:
                logger.error("Security DB not activated - policies cannot be loaded")
                return

            policies = db.get_all_policies()
            if not policies:
                logger.error("No policies found in database - check schema installation")
                return

            # Display policies
            display = policies.get('display', {})
            try:
                self._display_min_cvss = float(display.get('min_cvss', 0))
            except (ValueError, TypeError):
                self._display_min_cvss = 0.0

            severity = display.get('min_severity', 'None')
            self._display_min_severity = severity if severity in self.SEVERITY_LEVELS else 'None'
            self._display_show_patched = display.get('show_patched', True) in (True, 'true', '1', 1)

            try:
                self._display_max_age_days = int(display.get('max_age_days', 365))
            except (ValueError, TypeError):
                self._display_max_age_days = 365

            try:
                self._display_min_published_year = int(display.get('min_published_year', 2020))
            except (ValueError, TypeError):
                self._display_min_published_year = 2020

            # Exclusion policies
            exclusions = policies.get('exclusions', {})
            self._excluded_vendors = self._parse_list(exclusions.get('vendors', []))
            self._excluded_names = self._parse_list(exclusions.get('names', []))
            self._excluded_cve_ids = self._parse_list(exclusions.get('cve_ids', []), str.upper)
            self._excluded_machines_ids = self._parse_int_list(exclusions.get('machines_ids', []))
            self._excluded_groups_ids = self._parse_int_list(exclusions.get('groups_ids', []))

            logger.debug("Loaded policies from database")
        except Exception as e:
            logger.error(f"Could not load DB policies: {e}")

    def check(self):
        pass

    def is_cve_central_configured(self):
        """Check if CVE Central is properly configured"""
        return bool(self.cve_central_url and
                    self.cve_central_server_id and
                    self.cve_central_keyAES32)

    def get_severity_index(self, severity):
        """Get numeric index for severity level (for comparison)"""
        try:
            return self.SEVERITY_LEVELS.index(severity)
        except ValueError:
            return 0

    def should_display_cve(self, cve):
        """
        Check if a CVE should be displayed based on local policies.

        Args:
            cve: dict with keys: cve_id, cvss_score, severity, has_patch, published_date

        Returns:
            bool: True if CVE passes all display filters
        """
        self._ensure_db_policies_loaded()

        # Check CVSS score filter
        cvss = cve.get('cvss_score') or 0.0
        if isinstance(cvss, str):
            try:
                cvss = float(cvss)
            except (ValueError, TypeError):
                cvss = 0.0
        if cvss < self.display_min_cvss:
            return False

        # Check severity filter
        severity = cve.get('severity', 'None')
        if self.get_severity_index(severity) < self.get_severity_index(self.display_min_severity):
            return False

        # Check patched CVE filter
        if not self.display_show_patched and cve.get('has_patch'):
            return False

        # Check CVE ID exclusion
        cve_id = cve.get('cve_id', '').upper()
        if cve_id in self.excluded_cve_ids:
            return False

        return True

    def get_display_policies(self):
        """Return display policies as a dict (for API/UI)

        Note: Numeric values returned as strings for XMLRPC compatibility.
        """
        self._ensure_db_policies_loaded()
        return {
            'min_cvss': str(self.display_min_cvss),
            'min_severity': self.display_min_severity,
            'show_patched': self.display_show_patched,
            'max_age_days': str(self.display_max_age_days),
            'min_published_year': str(self.display_min_published_year)
        }

    def get_exclusion_policies(self):
        """Return exclusion policies as a dict (for API/UI)"""
        self._ensure_db_policies_loaded()
        return {
            'vendors': self.excluded_vendors,
            'names': self.excluded_names,
            'cve_ids': self.excluded_cve_ids,
            'machines_ids': self.excluded_machines_ids,
            'groups_ids': self.excluded_groups_ids
        }

    @staticmethod
    def activate():
        SecurityConfig("security")
        return True
