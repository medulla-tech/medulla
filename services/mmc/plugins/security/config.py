# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.security.config import SecurityDatabaseConfig
import json
import logging

logger = logging.getLogger()


class SecurityConfig(PluginConfig, SecurityDatabaseConfig):
    """
    Security plugin configuration.

    Configuration priority (highest to lowest):
    1. Database (policies table) - for [display], [policy], [exclusions]
    2. /etc/mmc/plugins/security.ini.local
    3. /etc/mmc/plugins/security.ini

    Note: [main] and [cve_central] sections are ONLY read from .ini files
    for security reasons (prevent UI tampering with credentials).
    """

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

    # Valid severity levels in order
    SEVERITY_LEVELS = ['None', 'Low', 'Medium', 'High', 'Critical']

    def setDefault(self):
        PluginConfig.setDefault(self)
        # Logging
        self.log_level = 'INFO'
        # CVE Central connection
        self.cve_central_url = ''
        self.cve_central_server_id = ''
        self.cve_central_keyAES32 = ''
        # Display settings
        self.display_min_cvss = 0.0
        self.display_min_severity = 'None'  # None, Low, Medium, High, Critical
        self.display_per_product_limit = 50
        self.display_show_patched = True  # Show CVEs with available patches
        # Policy defaults
        self.alert_min_cvss = 9.0
        self.alert_min_severity = 'Critical'  # Minimum severity for alerts
        self.alert_on_new = True  # Alert on new CVEs
        self.max_age_days = 365
        self.min_published_year = 2020
        # Exclusions (read from ini file)
        self.excluded_patterns = []
        self.excluded_vendors = []
        self.excluded_names = []
        self.excluded_cve_ids = []  # Specific CVE IDs to exclude

    def readConf(self):
        PluginConfig.readConf(self)
        SecurityDatabaseConfig.setup(self, self.conffile)

        # [main] section
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.safe_get("main", "tempdir", "/tmp/mmc-security")
        self.log_level = self.safe_get("main", "log_level", "INFO").upper()

        # [cve_central] section
        if self.has_section("cve_central"):
            self.cve_central_url = self.safe_get("cve_central", "url", "")
            self.cve_central_server_id = self.safe_get("cve_central", "server_id", "")
            self.cve_central_keyAES32 = self.safe_get("cve_central", "keyAES32", "")

        # [display] section
        if self.has_section("display"):
            try:
                self.display_min_cvss = float(self.safe_get("display", "min_cvss", "0.0"))
            except ValueError:
                self.display_min_cvss = 0.0

            severity = self.safe_get("display", "min_severity", "None")
            if severity in self.SEVERITY_LEVELS:
                self.display_min_severity = severity
            else:
                self.display_min_severity = 'None'

            try:
                self.display_per_product_limit = int(self.safe_get("display", "per_product_limit", "50"))
            except ValueError:
                self.display_per_product_limit = 50

            show_patched = self.safe_get("display", "show_patched", "true").lower()
            self.display_show_patched = show_patched in ('true', '1', 'yes', 'on')

        # [policy] section
        if self.has_section("policy"):
            try:
                self.alert_min_cvss = float(self.safe_get("policy", "alert_min_cvss", "9.0"))
            except ValueError:
                self.alert_min_cvss = 9.0

            alert_severity = self.safe_get("policy", "alert_min_severity", "Critical")
            if alert_severity in self.SEVERITY_LEVELS:
                self.alert_min_severity = alert_severity
            else:
                self.alert_min_severity = 'Critical'

            alert_on_new = self.safe_get("policy", "alert_on_new", "true").lower()
            self.alert_on_new = alert_on_new in ('true', '1', 'yes', 'on')

            try:
                self.max_age_days = int(self.safe_get("policy", "max_age_days", "365"))
            except ValueError:
                self.max_age_days = 365
            try:
                self.min_published_year = int(self.safe_get("policy", "min_published_year", "2020"))
            except ValueError:
                self.min_published_year = 2020

        # [exclusions] section
        if self.has_section("exclusions"):
            patterns = self.safe_get("exclusions", "patterns", "medulla,pulse,siveo")
            self.excluded_patterns = [p.strip() for p in patterns.split(',') if p.strip()]

            vendors = self.safe_get("exclusions", "vendors", "")
            self.excluded_vendors = [v.strip() for v in vendors.split(',') if v.strip()]

            names = self.safe_get("exclusions", "names", "")
            self.excluded_names = [n.strip() for n in names.split(',') if n.strip()]

            cve_ids = self.safe_get("exclusions", "cve_ids", "")
            self.excluded_cve_ids = [c.strip().upper() for c in cve_ids.split(',') if c.strip()]

    def safe_get(self, section, option, default=''):
        """Get config value with fallback to default"""
        try:
            return self.get(section, option)
        except:
            return default

    def _load_db_policies(self):
        """Load policies from database, overriding ini file values.

        Only loads [display], [policy], [exclusions] sections.
        [main] and [cve_central] remain from ini files only.
        """
        try:
            from pulse2.database.security import SecurityDatabase
            db = SecurityDatabase()
            if not db.is_activated:
                return  # DB not ready yet

            policies = db.get_all_policies()
            if not policies:
                return

            # Apply display policies
            if 'display' in policies:
                display = policies['display']
                if 'min_cvss' in display:
                    try:
                        self.display_min_cvss = float(display['min_cvss'])
                    except (ValueError, TypeError):
                        pass
                if 'min_severity' in display:
                    if display['min_severity'] in self.SEVERITY_LEVELS:
                        self.display_min_severity = display['min_severity']
                if 'per_product_limit' in display:
                    try:
                        self.display_per_product_limit = int(display['per_product_limit'])
                    except (ValueError, TypeError):
                        pass
                if 'show_patched' in display:
                    self.display_show_patched = display['show_patched'] in (True, 'true', '1', 1)

            # Apply policy settings
            if 'policy' in policies:
                policy = policies['policy']
                if 'alert_min_cvss' in policy:
                    try:
                        self.alert_min_cvss = float(policy['alert_min_cvss'])
                    except (ValueError, TypeError):
                        pass
                if 'alert_min_severity' in policy:
                    if policy['alert_min_severity'] in self.SEVERITY_LEVELS:
                        self.alert_min_severity = policy['alert_min_severity']
                if 'alert_on_new' in policy:
                    self.alert_on_new = policy['alert_on_new'] in (True, 'true', '1', 1)
                if 'max_age_days' in policy:
                    try:
                        self.max_age_days = int(policy['max_age_days'])
                    except (ValueError, TypeError):
                        pass
                if 'min_published_year' in policy:
                    try:
                        self.min_published_year = int(policy['min_published_year'])
                    except (ValueError, TypeError):
                        pass

            # Apply exclusions
            if 'exclusions' in policies:
                exclusions = policies['exclusions']
                if 'patterns' in exclusions:
                    val = exclusions['patterns']
                    if isinstance(val, list):
                        self.excluded_patterns = val
                    elif isinstance(val, str) and val:
                        self.excluded_patterns = [p.strip() for p in val.split(',') if p.strip()]
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
            # Silently fail - use ini values as fallback
            logger.debug(f"Could not load DB policies (using ini): {e}")

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

    def should_alert_cve(self, cve):
        """
        Check if a CVE should trigger an alert based on policies.

        Args:
            cve: dict with keys: cve_id, cvss_score, severity

        Returns:
            bool: True if CVE should trigger alert
        """
        self._ensure_db_policies_loaded()
        cvss = cve.get('cvss_score') or 0.0
        if isinstance(cvss, str):
            try:
                cvss = float(cvss)
            except (ValueError, TypeError):
                cvss = 0.0
        severity = cve.get('severity', 'None')

        # Alert if CVSS >= threshold OR severity >= threshold
        if cvss >= self.alert_min_cvss:
            return True
        if self.get_severity_index(severity) >= self.get_severity_index(self.alert_min_severity):
            return True

        return False

    def get_display_policies(self):
        """Return display policies as a dict (for API/UI)"""
        self._ensure_db_policies_loaded()
        return {
            'min_cvss': self.display_min_cvss,
            'min_severity': self.display_min_severity,
            'per_product_limit': self.display_per_product_limit,
            'show_patched': self.display_show_patched
        }

    def get_alert_policies(self):
        """Return alert policies as a dict (for API/UI)"""
        self._ensure_db_policies_loaded()
        return {
            'min_cvss': self.alert_min_cvss,
            'min_severity': self.alert_min_severity,
            'alert_on_new': self.alert_on_new
        }

    def get_exclusion_policies(self):
        """Return exclusion policies as a dict (for API/UI)"""
        self._ensure_db_policies_loaded()
        return {
            'patterns': self.excluded_patterns,
            'vendors': self.excluded_vendors,
            'names': self.excluded_names,
            'cve_ids': self.excluded_cve_ids
        }

    @staticmethod
    def activate():
        SecurityConfig("security")
        return True
