# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/glpi_adapter.py

"""Read-only GLPI REST adapter for itsmlocal-sync."""

import time
from collections.abc import Iterable
from typing import Any

import requests

from pulse2.itsmlocal_sync.adapters import ItsmAdapter, ItsmSnapshot, register_adapter


@register_adapter
class GLPIAdapter(ItsmAdapter):
    """Fetch normalized business data from a GLPI REST API source."""

    adapter_name = "glpi"

    def __init__(self, client_id: str, config: dict[str, Any], logger):
        super().__init__(client_id, config, logger)
        self.base_url = self._normalize_url(
            config.get("conn.api_url") or config.get("api_url")
        )
        self.app_token = config.get("auth.app_token") or config.get("app_token")
        self.user_token = config.get("auth.user_token") or config.get("user_token")
        self.timeout = int(config.get("conn.timeout") or config.get("timeout") or 60)
        self.session_token: str | None = None

    @staticmethod
    def _normalize_url(raw_url: Any) -> str:
        """Return a GLPI REST endpoint URL ending with apirest.php or api.php/v1."""
        url = str(raw_url or "").strip().rstrip("/")
        if not url:
            return ""
        if url.endswith("/apirest.php") or url.endswith("/api.php/v1"):
            return url
        return url + "/apirest.php"

    def _headers(self) -> dict[str, str]:
        """Return authenticated GLPI REST headers."""
        if not self.session_token:
            raise RuntimeError("GLPI session is not initialized")
        return {
            "App-Token": str(self.app_token),
            "Session-Token": str(self.session_token),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _do_get(
        self, url: str, headers: dict[str, str], label: str = ""
    ) -> requests.Response:
        """Run a GET request and log it (method, URL, status, latency)."""
        started = time.monotonic()
        response = requests.get(url, headers=headers, timeout=self.timeout)
        self.logger.debug(
            "GLPI %s GET %s -> %s (%.0f ms)%s",
            self.client_id,
            url,
            response.status_code,
            (time.monotonic() - started) * 1000,
            f" [{label}]" if label else "",
        )
        return response

    def _get_paginated(
        self, endpoint: str, page_size: int = 200
    ) -> list[dict[str, Any]]:
        """Fetch a paginated GLPI collection."""
        items: list[dict[str, Any]] = []
        offset = 0
        while True:
            separator = "&" if "?" in endpoint else "?"
            url = f"{self.base_url}/{endpoint}{separator}range={offset}-{offset + page_size - 1}"
            response = self._do_get(url, self._headers(), label=endpoint)
            if response.status_code == 416:
                break
            response.raise_for_status()
            chunk = response.json()
            if not isinstance(chunk, list) or not chunk:
                break
            items.extend(chunk)
            self.logger.debug(
                "GLPI %s %s: page %s-%s +%d (running total %d)",
                self.client_id,
                endpoint,
                offset,
                offset + page_size - 1,
                len(chunk),
                len(items),
            )
            content_range = response.headers.get("Content-Range", "")
            total = None
            if "/" in content_range:
                try:
                    total = int(content_range.split("/", 1)[1])
                except (TypeError, ValueError):
                    total = None
            if total is not None and len(items) >= total:
                break
            if len(chunk) < page_size:
                break
            offset += page_size
        return items

    def init_session(self) -> None:
        """Open a GLPI REST session."""
        if not self.base_url:
            raise RuntimeError("GLPI API URL is missing")
        if not self.app_token or not self.user_token:
            raise RuntimeError("GLPI app token or user token is missing")

        headers_variants = (
            {"Authorization": f"user_token {self.user_token}"},
            {"User-Token": str(self.user_token)},
            {"Authorization": f"Bearer {self.user_token}"},
        )
        base_headers = {
            "App-Token": str(self.app_token),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        last_response = None
        for auth_headers in headers_variants:
            headers = dict(base_headers)
            headers.update(auth_headers)
            scheme = next(iter(auth_headers))
            response = self._do_get(
                f"{self.base_url}/initSession",
                headers,
                label=f"initSession/{scheme}",
            )
            last_response = response
            if response.status_code == 200:
                self.session_token = response.json().get("session_token")
                if self.session_token:
                    self.logger.info(
                        "GLPI %s: session opened (auth scheme %s)",
                        self.client_id,
                        scheme,
                    )
                    return
            if response.status_code not in (400, 401, 403):
                break

        details = (
            last_response.text[:500] if last_response is not None else "no response"
        )
        raise RuntimeError(
            f"unable to open GLPI session for {self.client_id}: {details}"
        )

    def kill_session(self) -> None:
        """Close the current GLPI REST session."""
        if not self.session_token:
            return
        try:
            self._do_get(
                f"{self.base_url}/killSession",
                self._headers(),
                label="killSession",
            )
        finally:
            self.session_token = None

    def check_connection(self) -> None:
        """Validate GLPI API access without fetching business objects."""
        self.init_session()
        try:
            self.logger.info(
                "GLPI %s source connection ready: endpoint=%s",
                self.client_id,
                self.base_url,
            )
        finally:
            self.kill_session()

    @staticmethod
    def _str_id(value: Any, default: str = "") -> str:
        """Stringify a GLPI id, keeping ``0`` (the root entity id) intact."""
        if value is None or value == "":
            return default
        return str(value)

    @classmethod
    def _normalize_entity(cls, row: dict[str, Any]) -> dict[str, Any]:
        """Normalize a GLPI entity row."""
        return {
            "source_id": cls._str_id(row.get("id")),
            "source_parent_id": cls._str_id(row.get("entities_id"), "0"),
            "name": row.get("name") or "",
            "path": row.get("completename") or row.get("name") or "",
            "source_updated_at": row.get("date_mod") or "",
        }

    @classmethod
    def _normalize_profile(cls, row: dict[str, Any]) -> dict[str, Any]:
        """Normalize a GLPI profile row."""
        return {
            "source_id": cls._str_id(row.get("id")),
            "name": row.get("name") or "",
            "source_updated_at": row.get("date_mod") or "",
        }

    @classmethod
    def _normalize_user(cls, row: dict[str, Any]) -> dict[str, Any]:
        """Normalize a GLPI user row."""
        return {
            "source_id": cls._str_id(row.get("id")),
            "login": row.get("name") or "",
            "email": row.get("email") or "",
            "firstname": row.get("firstname") or "",
            "lastname": row.get("realname") or "",
            "is_active": int(row.get("is_active") or 0),
            "default_entity_id": cls._str_id(row.get("entities_id"), "0"),
            "default_profile_id": cls._str_id(row.get("profiles_id"), "0"),
            "source_updated_at": row.get("date_mod") or "",
        }

    def _get_user_scopes(self, user_ids: Iterable[str]) -> list[dict[str, Any]]:
        """Fetch user/profile/entity associations for selected users."""
        scopes: list[dict[str, Any]] = []
        user_ids = [uid for uid in user_ids if uid]
        self.logger.debug(
            "GLPI %s: fetching Profile_User for %d user(s)",
            self.client_id,
            len(user_ids),
        )
        for user_id in user_ids:
            response = self._do_get(
                f"{self.base_url}/User/{user_id}/Profile_User",
                self._headers(),
                label="Profile_User",
            )
            if response.status_code == 404:
                continue
            response.raise_for_status()
            rows = response.json()
            if isinstance(rows, dict):
                rows = [rows]
            if not isinstance(rows, list):
                continue
            for row in rows:
                scopes.append(
                    {
                        "source_user_id": str(user_id),
                        "source_profile_id": str(row.get("profiles_id") or ""),
                        "source_entity_id": str(row.get("entities_id") or "0"),
                        "is_recursive": int(row.get("is_recursive") or 0),
                        "is_default": int(
                            row.get("is_default_profile") or row.get("is_default") or 0
                        ),
                    }
                )
        return scopes

    def fetch_snapshot(self) -> ItsmSnapshot:
        """Fetch and normalize GLPI entities, users, profiles and scopes."""
        started = time.monotonic()
        self.init_session()
        try:
            entities = [
                self._normalize_entity(row) for row in self._get_paginated("Entity")
            ]
            users = [self._normalize_user(row) for row in self._get_paginated("User")]
            profiles = [
                self._normalize_profile(row) for row in self._get_paginated("Profile")
            ]
            user_scopes = self._get_user_scopes(user["source_id"] for user in users)
            self.logger.info(
                "GLPI %s snapshot: %d entities, %d users, %d profiles, "
                "%d user scopes (%.1fs)",
                self.client_id,
                len(entities),
                len(users),
                len(profiles),
                len(user_scopes),
                time.monotonic() - started,
            )
            return ItsmSnapshot(
                entities=entities,
                users=users,
                profiles=profiles,
                user_scopes=user_scopes,
            )
        finally:
            self.kill_session()
