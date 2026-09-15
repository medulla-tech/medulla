# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/ldap_local_adapter.py

"""Read-only adapter turning the Medulla local LDAP into an ITSM snapshot.

Unlike the other adapters (GLPI, ServiceNow...), the source here is not a
remote ITSM owned by a client: it is Medulla's own local LDAP (``slapd``),
already fed by the existing authentication/provisioning flows (baseldap,
externalldap, OIDC). Every ``uid`` is already guaranteed unique by LDAP
itself, so this adapter asks ``reconcile.py`` to keep the raw login instead
of the collision-free technical login used for external ITSM sources (set
``config["preserve_login"] = True``).

Phase 1 scope (single organisation): all users are attached to one synthetic
root entity and no profile is resolved yet (``reconcile.py`` falls back to
the ``Self-Service`` profile). Per-client entity attribution and ACL-based
profile fabrication are later phases (see doc/ldap_auth/09_PLAN_ACTION.md).
"""

from typing import Any

import ldap

from pulse2.itsmlocal_sync.adapters import ItsmAdapter, ItsmSnapshot, register_adapter

ROOT_SOURCE_ID = "0"
ROOT_ENTITY_NAME = "LDAP local"


@register_adapter
class LDAPLocalAdapter(ItsmAdapter):
    """Fetch normalized business data from the Medulla local LDAP."""

    adapter_name = "ldap_local"

    def __init__(self, client_id: str, config: dict[str, Any], logger):
        super().__init__(client_id, config, logger)
        self.ldap_url = config.get("conn.ldap_url") or config.get("ldapurl") or "ldap://127.0.0.1:389"
        self.users_dn = config.get("conn.users_dn") or config.get("baseusersdn")
        self.bind_dn = config.get("auth.bind_dn") or config.get("rootname")
        self.bind_password = config.get("auth.bind_password") or config.get("password")
        self.timeout = int(config.get("conn.timeout") or config.get("network_timeout") or 30)
        self._connection = None

    def _connect(self):
        """Open (and cache) a bound LDAP connection to the local directory."""
        if self._connection is not None:
            return self._connection
        if not self.users_dn or not self.bind_dn:
            raise RuntimeError(
                "LDAP local adapter: missing conn.users_dn/auth.bind_dn configuration"
            )
        connection = ldap.initialize(self.ldap_url)
        connection.set_option(ldap.OPT_REFERRALS, ldap.OPT_OFF)
        connection.set_option(ldap.OPT_NETWORK_TIMEOUT, self.timeout)
        connection.simple_bind_s(self.bind_dn, self.bind_password)
        self._connection = connection
        return connection

    def check_connection(self) -> None:
        """Validate the local LDAP bind without fetching business objects."""
        self._connect()
        self.logger.info(
            "LDAP local %s source connection ready: url=%s users_dn=%s",
            self.client_id,
            self.ldap_url,
            self.users_dn,
        )

    @staticmethod
    def _first(attrs: dict[str, list[bytes]], name: str) -> str:
        """Return the first LDAP attribute value decoded as text, or ''."""
        values = attrs.get(name) or []
        if not values:
            return ""
        value = values[0]
        return value.decode("utf-8") if isinstance(value, bytes) else str(value)

    def _fetch_users(self) -> list[dict[str, Any]]:
        """Read every user entry under ``users_dn`` and normalize it."""
        connection = self._connect()
        results = connection.search_s(
            self.users_dn,
            ldap.SCOPE_SUBTREE,
            "(objectClass=inetOrgPerson)",
            ["uid", "sn", "givenName", "mail"],
        )
        users = []
        for _dn, attrs in results:
            if not isinstance(attrs, dict):
                # Malformed LDAP entry (already seen with misconfigured
                # AD/LDAP servers, cf. LDAP_AD_FIX.patch): skip, don't crash.
                self.logger.warning("LDAP local %s: skipping malformed entry", self.client_id)
                continue
            uid = self._first(attrs, "uid")
            if not uid:
                continue
            users.append(
                {
                    "source_id": uid,
                    "login": uid,
                    "email": self._first(attrs, "mail"),
                    "firstname": self._first(attrs, "givenName"),
                    "lastname": self._first(attrs, "sn"),
                    "is_active": 1,
                    "default_entity_id": ROOT_SOURCE_ID,
                    "default_profile_id": "",
                }
            )
        return users

    def fetch_snapshot(self) -> ItsmSnapshot:
        """Fetch and normalize the local LDAP as a single-entity snapshot."""
        users = self._fetch_users()
        entities = [
            {
                "source_id": ROOT_SOURCE_ID,
                "source_parent_id": ROOT_SOURCE_ID,
                "name": ROOT_ENTITY_NAME,
                "path": ROOT_ENTITY_NAME,
                "source_updated_at": "",
            }
        ]
        self.logger.info(
            "LDAP local %s snapshot: %d entities, %d users",
            self.client_id,
            len(entities),
            len(users),
        )
        return ItsmSnapshot(entities=entities, users=users, profiles=[], user_scopes=[])
