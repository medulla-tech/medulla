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
    """

    # Valid severity levels in order
    SEVERITY_LEVELS = ['None', 'Low', 'Medium', 'High', 'Critical']

    # Default values for policies (matching schema-001.sql defaults)
    DEFAULT_POLICIES = {
        'display': {
            'min_cvss': '4.0',
            'min_severity': 'Medium',
            'show_patched': True,
            'max_age_days': '365',
            'min_published_year': '2020'
        },
        'exclusions': {
            'vendors': [],
            'names': [],
            'cve_ids': []
        }
    }

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

    def setDefault(self):
        PluginConfig.setDefault(self)
        # Logging
        self.log_level = 'INFO'
        # CVE Central connection
        self.cve_central_url = ''
        self.cve_central_server_id = ''
        self.cve_central_keyAES32 = ''
        self.use_websocket = True

        # Display filters (defaults from schema-001.sql)
        self.display_min_cvss = 4.0
        self.display_min_severity = 'Medium'
        self.display_show_patched = True
        self.display_max_age_days = 365
        self.display_min_published_year = 2020

        # Exclusions (empty by default)
        self.excluded_vendors = []
        self.excluded_names = []
        self.excluded_cve_ids = []

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

    def _load_db_policies(self):
        """Load policies from database.

        Display and exclusion policies are stored in the policies table.
        If no values in DB, defaults from DEFAULT_POLICIES are used.
        """
        try:
            from pulse2.database.security import SecurityDatabase
            db = SecurityDatabase()
            if not db.is_activated:
                logger.debug("DB not activated, using default policies")
                return

            policies = db.get_all_policies()

            # Apply display policies from DB (or keep defaults)
            if policies and 'display' in policies:
                display = policies['display']
                if 'min_cvss' in display:
                    try:
                        self.display_min_cvss = float(display['min_cvss'])
                    except (ValueError, TypeError):
                        pass
                if 'min_severity' in display:
                    if display['min_severity'] in self.SEVERITY_LEVELS:
                        self.display_min_severity = display['min_severity']
                if 'show_patched' in display:
                    self.display_show_patched = display['show_patched'] in (True, 'true', '1', 1)
                if 'max_age_days' in display:
                    try:
                        self.display_max_age_days = int(display['max_age_days'])
                    except (ValueError, TypeError):
                        pass
                if 'min_published_year' in display:
                    try:
                        self.display_min_published_year = int(display['min_published_year'])
                    except (ValueError, TypeError):
                        pass

            # Apply exclusions from DB (or keep defaults)
            if policies and 'exclusions' in policies:
                exclusions = policies['exclusions']
                if 'vendors' in exclusions:
                    val = exclusions['vendors']
                    if isinstance(val, list):
                        self.excluded_vendors = val
                    elif isinstance(val, str) and val:
                        self.excluded_vendors = [v.strip() for v in val.split(',') if v.strip()]
                if 'names' in exclusions:
                    val = exclusions['names']
                    if isinstance(val, list):
                        self.excluded_names = val
                    elif isinstance(val, str) and val:
                        self.excluded_names = [n.strip() for n in val.split(',') if n.strip()]
                if 'cve_ids' in exclusions:
                    val = exclusions['cve_ids']
                    if isinstance(val, list):
                        self.excluded_cve_ids = [c.upper() for c in val]
                    elif isinstance(val, str) and val:
                        self.excluded_cve_ids = [c.strip().upper() for c in val.split(',') if c.strip()]

            logger.debug("Loaded policies from database")
        except Exception as e:
            logger.warning(f"Could not load DB policies, using defaults: {e}")

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
            'cve_ids': self.excluded_cve_ids
        }

    @staticmethod
    def activate():
        SecurityConfig("security")
        return True
