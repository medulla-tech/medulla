# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Configuration of the reflex plugin.

Only what has to be known before a connection exists: the database section,
the encryption key of the channel secrets and disable. The operating
settings live in the settings table, the channels in the database.
"""

import logging
import os
import secrets
import string

from mmc.support.config import PluginConfig
from pulse2.database.reflex.config import ReflexDatabaseConfig

logger = logging.getLogger()


class ReflexConfig(PluginConfig, ReflexDatabaseConfig):
    """Reflex plugin configuration."""

    def __init__(self, name='reflex', conffile=None, backend="ini"):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile, backend=backend)
            ReflexDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        # [main]
        self.disable = True
        self.keyAES32 = ""

    def readConf(self):
        PluginConfig.readConf(self)
        if self.conffile and self.backend == "ini":
            ReflexDatabaseConfig.setup(self, self.conffile)

        self.disable = self.safe_getboolean("main", "disable", True)
        # Key of the channel secrets.
        self.keyAES32 = self.safe_get("main", "keyAES32", "")

    # =========================================================================
    # Readers tolerant to a missing option
    # =========================================================================
    def safe_get(self, section, option, default=''):
        try:
            value = self.get(section, option)
        except Exception:
            return default
        return default if value is None else value

    def safe_getboolean(self, section, option, default=False):
        try:
            value = str(self.get(section, option)).strip().lower()
        except Exception:
            return default
        if value in ('1', 'true', 'yes', 'on'):
            return True
        if value in ('0', 'false', 'no', 'off'):
            return False
        return default

    # =========================================================================
    # Channel secrets
    # =========================================================================
    def ensure_aes_key(self):
        """Return a usable encryption key, generating it on first need."""
        if self.has_aes_key():
            return str(self.keyAES32)

        alphabet = string.ascii_letters + string.digits
        key = ''.join(secrets.choice(alphabet) for _ in range(32))

        local = "%s.local" % (self.conffile or "/etc/mmc/plugins/reflex.ini")
        try:
            existing = ""
            if os.path.isfile(local):
                with open(local, "r") as handle:
                    existing = handle.read()

            if "[main]" in existing:
                block = "[main]\nkeyAES32 = %s" % key
                content = existing.replace("[main]", block, 1)
            else:
                separator = "" if existing.endswith("\n") or not existing else "\n"
                content = "%s%s\n[main]\nkeyAES32 = %s\n" % (existing, separator, key)

            with open(local, "w") as handle:
                handle.write(content)
            os.chmod(local, 0o600)
        except (IOError, OSError) as exc:
            logger.error(
                "Plugin reflex: could not write the encryption key to %s (%s). "
                "Channel passwords cannot be stored until keyAES32 is set by hand.",
                local, exc)
            return ""

        self.keyAES32 = key
        logger.info("Plugin reflex: encryption key generated in %s", local)
        return key

    def has_aes_key(self):
        """Whether a usable encryption key is configured."""
        return len(str(self.keyAES32 or '').encode('utf-8')) == 32

    def check(self):
        pass

    @staticmethod
    def activate():
        ReflexConfig("reflex")
        return True
