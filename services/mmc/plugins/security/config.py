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

    def __init__(self, name='security', conffile=None, backend="ini"):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="security_conf")
            SecurityDatabaseConfig.__init__(self)
            self.initdone = True
            self._db_policies_loaded = False

    def _ensure_db_policies_loaded(self):
        """Lazy load DB policies on first access."""
        if not self._db_policies_loaded:
            self.load_policies()
            self._db_policies_loaded = True

    # Attributes that trigger lazy loading from DB
    _POLICY_ATTRS = {
        'display_min_severity', 'display_show_unfixed',
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
        self.cve_central_ssl_verify = True

    def __getattr__(self, name):
        """Lazy load policies from DB on first access to policy attributes."""
        if name in self._POLICY_ATTRS:
            self._ensure_db_policies_loaded()
            # After loading, the attribute should exist with _ prefix
            return getattr(self, f'_{name}')
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def readConf(self):
        PluginConfig.readConf(self)
        if self.backend == "database":
            self._load_db_settings_from_backend()
        elif self.conffile and self.backend == "ini":
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
            self.cve_central_ssl_verify = self.safe_get("cve_central", "ssl_verify", "1") not in ('0', 'false', 'no')

        # NOTE: [display] and [exclusions] are NOT read from .ini
        # They are loaded from database via load_policies()

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

    def load_policies(self):
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
            severity = display.get('min_severity', 'None')
            self._display_min_severity = severity if severity in self.SEVERITY_LEVELS else 'None'
            self._display_show_unfixed = display.get('show_unfixed', False) in (True, 'true', '1', 1)

            # 0 = pas de limite (défaut, et valeur illisible)
            try:
                self._display_max_age_days = int(display.get('max_age_days', 0))
            except (ValueError, TypeError):
                self._display_max_age_days = 0

            try:
                self._display_min_published_year = int(display.get('min_published_year', 0))
            except (ValueError, TypeError):
                self._display_min_published_year = 0

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

    def filters(self):
        """Display policies as keyword arguments of the SecurityDatabase reads."""
        self.load_policies()  # toujours relu : mmc-agent garde cette config en mémoire
        return {
            'min_severity': self.display_min_severity,
            'excluded_names': self.excluded_names,
            'excluded_cve_ids': self.excluded_cve_ids,
            'excluded_machines_ids': self.excluded_machines_ids,
            'excluded_groups_ids': self.excluded_groups_ids,
            'show_unfixed': self.display_show_unfixed,
            'max_age_days': self.display_max_age_days,
            'min_published_year': self.display_min_published_year
        }

    def get_display_policies(self):
        """Return display policies as a dict (for API/UI)

        Note: Numeric values returned as strings for XMLRPC compatibility.
        """
        self.load_policies()  # toujours relu : mmc-agent garde cette config en mémoire
        return {
            'min_severity': self.display_min_severity,
            'show_unfixed': self.display_show_unfixed,
            'max_age_days': str(self.display_max_age_days),
            'min_published_year': str(self.display_min_published_year)
        }

    def get_exclusion_policies(self):
        """Return exclusion policies as a dict (for API/UI)"""
        self.load_policies()  # toujours relu : mmc-agent garde cette config en mémoire
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

