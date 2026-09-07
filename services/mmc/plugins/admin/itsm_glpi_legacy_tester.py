# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later

"""Dedicated legacy GLPI API REST connection tester.

This module is intentionally isolated from production GLPI client classes.
It only orchestrates how they are used for ITSM form connection checks.
"""

import os
import re
import logging
from contextlib import contextmanager

try:
    from mmc.support.apirest.glpi import GLPIClient, GLPIAPIError
except ImportError:
    from mmc.support.apirest.glpi import GLPIClient

    class GLPIAPIError(RuntimeError):
        pass


logger = logging.getLogger()


class GLPIApiRestLegacyConnectionTester:
    """Run a connection test against GLPI legacy API REST endpoint only."""

    _PROXY_ENV_KEYS = (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    )

    def __init__(self, api_url, app_token, user_token):
        self.api_url = str(api_url or "").strip()
        self.app_token = str(app_token or "").strip()
        self.user_token = str(user_token or "").strip()

    @staticmethod
    def _mask(value):
        txt = str(value or "")
        if not txt:
            return "<empty>"
        if len(txt) <= 8:
            return "*" * len(txt)
        return txt[:4] + "***" + txt[-4:]

    @staticmethod
    def normalize_legacy_url(raw_url):
        """Normalize URL from form input to a valid apirest.php endpoint."""
        url = str(raw_url or "").strip()
        if not url:
            return ""

        # Fix accidental '/.' suffix.
        while url.endswith("/."):
            url = url[:-2]

        # Collapse repeated slashes while preserving scheme.
        url = re.sub(r"(?<!:)/{2,}", "/", url)

        lower_url = url.lower()
        if "apirest.php" in lower_url:
            # Trim anything after apirest.php and remove trailing slash.
            idx = lower_url.find("apirest.php")
            url = url[: idx + len("apirest.php")]
            return url.rstrip("/")

        # If GLPI root was provided, force legacy endpoint.
        return url.rstrip("/") + "/apirest.php"

    @contextmanager
    def _without_env_proxies(self):
        """Prevent environment proxies from hijacking test requests."""
        saved = {k: os.environ.get(k) for k in self._PROXY_ENV_KEYS}
        saved_no_proxy = os.environ.get("NO_PROXY")
        try:
            for key in self._PROXY_ENV_KEYS:
                os.environ.pop(key, None)
            os.environ["NO_PROXY"] = "*"
            yield
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            if saved_no_proxy is None:
                os.environ.pop("NO_PROXY", None)
            else:
                os.environ["NO_PROXY"] = saved_no_proxy

    def test(self):
        logger.info(
            "[ITSM_GLPI_LEGACY_TEST] start url=%s app_token=%s user_token=%s",
            self.api_url,
            self._mask(self.app_token),
            self._mask(self.user_token),
        )
        if not self.api_url:
            logger.warning("[ITSM_GLPI_LEGACY_TEST] missing api_url")
            return {"success": False, "message": "API URL not provided"}
        if not self.app_token or not self.user_token:
            logger.warning("[ITSM_GLPI_LEGACY_TEST] missing tokens")
            return {"success": False, "message": "Authentication credentials missing"}

        candidate_url = self.normalize_legacy_url(self.api_url)
        logger.info("[ITSM_GLPI_LEGACY_TEST] normalized_url=%s", candidate_url)
        if not candidate_url:
            logger.warning("[ITSM_GLPI_LEGACY_TEST] invalid normalized URL")
            return {"success": False, "message": "Invalid API URL"}

        client = None
        try:
            logger.info("[ITSM_GLPI_LEGACY_TEST] init GLPIClient url_base=%s", candidate_url)
            with self._without_env_proxies():
                client = GLPIClient(
                    app_token=self.app_token,
                    url_base=candidate_url,
                    user_token=self.user_token,
                )
                client.init_session()

            if hasattr(client, "SESSION_TOKEN") and client.SESSION_TOKEN:
                logger.info("[ITSM_GLPI_LEGACY_TEST] success session_token_present=true")
                return {
                    "success": True,
                    "message": f"GLPI legacy API REST connection successful ({candidate_url})",
                }
            logger.warning("[ITSM_GLPI_LEGACY_TEST] session_token missing")
            return {
                "success": False,
                "message": f"GLPI legacy API REST connection failed: missing session token ({candidate_url})",
            }
        except GLPIAPIError as e:
            logger.warning("[ITSM_GLPI_LEGACY_TEST] GLPIAPIError: %s", e)
            feedback = getattr(e, "feedback", None)
            if feedback is not None and hasattr(feedback, "to_dict"):
                logger.warning("[ITSM_GLPI_LEGACY_TEST] feedback=%s", feedback.to_dict())
                return {
                    "success": False,
                    "message": (
                        "GLPI legacy API REST connection failed "
                        f"({candidate_url}): {feedback.to_dict()}"
                    ),
                }
            return {
                "success": False,
                "message": f"GLPI legacy API REST connection failed ({candidate_url}): {e}",
            }
        except Exception as e:
            msg = str(e)
            if "Temporary failure in name resolution" in msg or "[Errno -3]" in msg:
                logger.warning("[ITSM_GLPI_LEGACY_TEST] DNS resolution failure for %s", candidate_url)
                return {
                    "success": False,
                    "message": (
                        "GLPI legacy API REST connection failed: DNS resolution error "
                        f"for host in URL ({candidate_url})"
                    ),
                }
            logger.warning("[ITSM_GLPI_LEGACY_TEST] exception: %s", e)
            return {
                "success": False,
                "message": f"GLPI legacy API REST connection failed ({candidate_url}): {e}",
            }
        finally:
            if client is not None:
                try:
                    client.kill_session()
                    logger.info("[ITSM_GLPI_LEGACY_TEST] kill_session done")
                except Exception:
                    logger.debug("GLPI legacy tester: kill_session failed", exc_info=True)
