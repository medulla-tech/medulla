# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/reconcile.py

"""Reconcile an ITSM snapshot into the itsmlocal target database.

For each client, Medulla owns a dedicated root entity in ``itsmlocal`` and
grafts the client organisation (entities) underneath it. The source ids are
never reused locally: every source entity gets a stable local id, recorded in
``admin.saas_itsm_entity_mapping`` (unique on ``client_id`` + ``source_id``).

Users receive distinct technical local logins scoped by ``client_id`` and
source user id. Their profile/entity assignments are written only when their
source entities are mapped inside the same client tree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from sqlalchemy import text

MEDULLA_ROOT_ID = 0
MEDULLA_ROOT_NAME = "Medulla"
ALLOC_LOCK = "itsmlocal_entity_alloc"
CLIENT_ROOT_KEY = "__client_root__"
LOCAL_LOGIN_PREFIX = "medulla__"
LOCAL_PROFILE_FALLBACK = "Self-Service"
# Business rule: a source ITSM profile can grant at most the Medulla client
# administrator role. The ITSMLocal platform Super-Admin role is reserved for
# the platform administrator and is never assigned by client synchronisation.
LOCAL_CLIENT_PROFILE_NAMES = frozenset(
    {
        "Self-Service",
        "Observer",
        "Admin",
        "Hotliner",
        "Technician",
        "Supervisor",
        "Read-Only",
    }
)
LOCAL_PROFILE_REMAP = {
    "super-admin": "Admin",
    "super admin": "Admin",
    "super-administrateur": "Admin",
    "super administrateur": "Admin",
    "self service": "Self-Service",
    "demandeur": "Self-Service",
    "read only": "Read-Only",
    "lecture seule": "Read-Only",
}


@dataclass
class ReconcileResult:
    """Counters returned by :func:`reconcile_client`."""

    created: int = 0
    updated: int = 0
    ignored: int = 0
    errors: list[str] = field(default_factory=list)

    def as_status(self) -> str:
        if self.errors:
            return "partial" if (self.created or self.updated) else "failed"
        return "success"


def _is_source_root(entity: dict[str, Any]) -> bool:
    """Return True for the source tree root (GLPI entity id 0)."""
    source_id = str(entity.get("source_id") or "")
    parent_id = str(entity.get("source_parent_id") or "0")
    return source_id in ("", "0") or parent_id == source_id


class _EntityWriter:
    """Small helper bound to one client and one transaction."""

    def __init__(self, connection, client_id: str, config_version: str, logger):
        self.connection = connection
        self.client_id = client_id
        self.config_version = config_version
        self.logger = logger

    def _alloc_id(self) -> int:
        row = self.connection.execute(
            text("SELECT COALESCE(MAX(`id`), 0) + 1 AS next_id FROM `glpi_entities`")
        ).scalar()
        return int(row or 1)

    def upsert_entity(
        self,
        local_id: int,
        name: str,
        parent_local_id: int,
        completename: str,
        level: int,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO `glpi_entities`
                    (`id`, `name`, `entities_id`, `completename`, `level`,
                     `sons_cache`, `ancestors_cache`, `date_mod`, `date_creation`)
                VALUES
                    (:id, :name, :parent, :completename, :level,
                     '[]', NULL, NOW(), NOW())
                ON DUPLICATE KEY UPDATE
                    `name` = VALUES(`name`),
                    `entities_id` = VALUES(`entities_id`),
                    `completename` = VALUES(`completename`),
                    `level` = VALUES(`level`),
                    `date_mod` = NOW()
                """
            ),
            {
                "id": local_id,
                "name": name,
                "parent": parent_local_id,
                "completename": completename,
                "level": level,
            },
        )

    def entity_exists(self, local_id: int) -> bool:
        return bool(
            self.connection.execute(
                text("SELECT 1 FROM `glpi_entities` WHERE `id` = :id"),
                {"id": local_id},
            ).first()
        )

    def find_by_parent_name(self, parent_local_id: int, name: str) -> int | None:
        """Return the local id of an existing sibling by (parent, name)."""
        row = self.connection.execute(
            text(
                "SELECT `id` FROM `glpi_entities` "
                "WHERE `entities_id` = :parent AND `name` = :name"
            ),
            {"parent": parent_local_id, "name": name},
        ).scalar()
        return int(row) if row is not None else None


def _load_mapping(admin_connection, client_id: str) -> dict[str, dict[str, Any]]:
    rows = admin_connection.execute(
        text(
            """
            SELECT `source_id`, `target_glpi_id`, `target_path`
            FROM `saas_itsm_entity_mapping`
            WHERE `client_id` = :client_id
            """
        ),
        {"client_id": client_id},
    ).mappings()
    return {str(row["source_id"]): dict(row) for row in rows}


def _save_mapping(
    admin_connection,
    client_id: str,
    source_id: str,
    source_path: str,
    target_path: str,
    target_glpi_id: int,
    config_version: str,
) -> None:
    admin_connection.execute(
        text(
            """
            INSERT INTO `saas_itsm_entity_mapping`
                (`client_id`, `source_path`, `source_id`, `target_path`,
                 `target_glpi_id`, `config_version`, `last_modifier`,
                 `modification_origin`)
            VALUES
                (:client_id, :source_path, :source_id, :target_path,
                 :target_glpi_id, :config_version, 'system_sync', 'sync')
            ON DUPLICATE KEY UPDATE
                `source_path` = VALUES(`source_path`),
                `target_path` = VALUES(`target_path`),
                `target_glpi_id` = VALUES(`target_glpi_id`),
                `config_version` = VALUES(`config_version`),
                `last_modifier` = VALUES(`last_modifier`),
                `modification_origin` = VALUES(`modification_origin`),
                `updated_at` = CURRENT_TIMESTAMP
            """
        ),
        {
            "client_id": client_id,
            "source_path": source_path[:500],
            "source_id": source_id,
            "target_path": target_path[:500],
            "target_glpi_id": target_glpi_id,
            "config_version": config_version[:50],
        },
    )


def _load_user_mapping(admin_connection, client_id: str) -> dict[str, dict[str, Any]]:
    """Return source-user mappings scoped to one ITSM client."""
    rows = admin_connection.execute(
        text(
            """
            SELECT `source_user_id`, `target_user_id`, `target_login`
            FROM `saas_itsm_user_mapping`
            WHERE `client_id` = :client_id
            """
        ),
        {"client_id": client_id},
    ).mappings()
    return {str(row["source_user_id"]): dict(row) for row in rows}


def _load_profile_mapping(admin_connection, client_id: str) -> dict[str, str]:
    """Return enabled Medulla-owned profile exceptions for one client.

    The source profile ID, rather than its mutable label, identifies an
    exception. Invalid targets are ignored so configuration cannot grant a
    platform-only role.
    """
    rows = admin_connection.execute(
        text(
            """
            SELECT `source_profile_id`, `target_profile_name`
            FROM `saas_itsm_profile_mapping`
            WHERE `client_id` = :client_id AND `enabled` = 1
            """
        ),
        {"client_id": client_id},
    ).mappings()
    return {
        str(row["source_profile_id"]): str(row["target_profile_name"])
        for row in rows
        if str(row["target_profile_name"]) in LOCAL_CLIENT_PROFILE_NAMES
    }


def _save_user_mapping(
    admin_connection,
    client_id: str,
    user: dict[str, Any],
    target_user_id: int,
    target_login: str,
) -> None:
    """Upsert one source-user to ITSMLocal mapping scoped by client id."""
    admin_connection.execute(
        text(
            """
            INSERT INTO `saas_itsm_user_mapping`
                (`client_id`, `source_user_id`, `source_login`, `source_email`,
                 `target_user_id`, `target_login`, `source_updated_at`, `last_seen_at`)
            VALUES
                (:client_id, :source_user_id, :source_login, :source_email,
                 :target_user_id, :target_login, :source_updated_at, NOW())
            ON DUPLICATE KEY UPDATE
                `source_login` = VALUES(`source_login`),
                `source_email` = VALUES(`source_email`),
                `target_user_id` = VALUES(`target_user_id`),
                `target_login` = VALUES(`target_login`),
                `source_updated_at` = VALUES(`source_updated_at`),
                `last_seen_at` = NOW()
            """
        ),
        {
            "client_id": client_id,
            "source_user_id": str(user.get("source_id") or ""),
            "source_login": str(user.get("login") or "")[:255],
            "source_email": str(user.get("email") or "")[:255],
            "target_user_id": target_user_id,
            "target_login": target_login,
            "source_updated_at": str(user.get("source_updated_at") or "")[:50],
        },
    )


def _local_login(client_id: str, source_user_id: str) -> str:
    """Return a collision-free technical login for one client source user."""
    digest = sha256(f"{client_id}:{source_user_id}".encode()).hexdigest()
    return f"{LOCAL_LOGIN_PREFIX}{digest}"


def _local_profile_name(
    source_name: str,
    source_profile_id: str = "",
    overrides: dict[str, str] | None = None,
) -> str:
    """Map a source profile to the bounded Medulla client profile set.

    A Medulla-owned exception keyed by source profile ID takes precedence when
    its target belongs to the allowed client set. Otherwise ``Super-Admin`` is
    mapped to ``Admin`` and unknown profiles receive the least privileged local
    profile rather than creating a profile or granting an implicit elevated role.
    """
    override = (overrides or {}).get(str(source_profile_id))
    if override in LOCAL_CLIENT_PROFILE_NAMES:
        return override
    source_name = str(source_name or "").strip()
    normalized_name = source_name.lower()
    if normalized_name in LOCAL_PROFILE_REMAP:
        return LOCAL_PROFILE_REMAP[normalized_name]
    if source_name in LOCAL_CLIENT_PROFILE_NAMES:
        return source_name
    return LOCAL_PROFILE_FALLBACK


def _local_profile_ids(connection) -> dict[str, int]:
    """Return the IDs of the predefined ITSMLocal client profiles."""
    rows = connection.execute(
        text("SELECT `id`, `name` FROM `glpi_profiles`")
    ).mappings()
    return {
        str(row["name"]): int(row["id"])
        for row in rows
        if str(row["name"]) in LOCAL_CLIENT_PROFILE_NAMES
    }


def _upsert_user(
    connection,
    user: dict[str, Any],
    local_login: str,
    default_entity_id: int,
    default_profile_id: int,
    mapped_user_id: int | None,
) -> tuple[int, bool]:
    """Create or update one technical ITSMLocal user without a password."""
    user_id = mapped_user_id
    if user_id:
        exists = connection.execute(
            text("SELECT 1 FROM `glpi_users` WHERE `id` = :id"), {"id": user_id}
        ).first()
        if not exists:
            user_id = None
    if not user_id:
        user_id = connection.execute(
            text(
                "SELECT `id` FROM `glpi_users` WHERE `name` = :name "
                "AND `authtype` = 0 AND `auths_id` = 0"
            ),
            {"name": local_login},
        ).scalar()
    is_update = user_id is not None
    values = {
        "name": local_login,
        "firstname": str(user.get("firstname") or "")[:255],
        "realname": str(user.get("lastname") or "")[:255],
        "is_active": 1 if int(user.get("is_active") or 0) else 0,
        "profiles_id": default_profile_id,
        "entities_id": default_entity_id,
    }
    if is_update:
        values["id"] = int(user_id)
        connection.execute(
            text(
                "UPDATE `glpi_users` SET `firstname` = :firstname, "
                "`realname` = :realname, `is_active` = :is_active, "
                "`profiles_id` = :profiles_id, `entities_id` = :entities_id, "
                "`date_mod` = NOW() WHERE `id` = :id"
            ),
            values,
        )
        return int(user_id), True

    result = connection.execute(
        text(
            "INSERT INTO `glpi_users` "
            "(`name`, `password`, `firstname`, `realname`, `is_active`, "
            "`profiles_id`, `entities_id`, `date_mod`, `date_creation`) "
            "VALUES (:name, NULL, :firstname, :realname, :is_active, "
            ":profiles_id, :entities_id, NOW(), NOW())"
        ),
        values,
    )
    return int(result.lastrowid), False


def _replace_user_scopes(
    connection, user_id: int, scopes: list[dict[str, int]]
) -> None:
    """Replace only profile assignments owned by the synchronized user."""
    connection.execute(
        text("DELETE FROM `glpi_profiles_users` WHERE `users_id` = :user_id"),
        {"user_id": user_id},
    )
    for scope in scopes:
        connection.execute(
            text(
                "INSERT INTO `glpi_profiles_users` "
                "(`users_id`, `profiles_id`, `entities_id`, `is_recursive`, "
                "`is_dynamic`, `is_default_profile`) "
                "VALUES (:user_id, :profile_id, :entity_id, :is_recursive, 0, :is_default)"
            ),
            {"user_id": user_id, **scope},
        )


def _upsert_user_email(connection, user_id: int, email: str) -> None:
    """Store a source email on its local technical user when one is supplied."""
    email = email.strip()[:255]
    if not email:
        return
    connection.execute(
        text(
            "INSERT INTO `glpi_useremails` (`users_id`, `email`, `is_default`, `is_dynamic`) "
            "VALUES (:user_id, :email, 1, 0) "
            "ON DUPLICATE KEY UPDATE `is_default` = 1, `is_dynamic` = 0"
        ),
        {"user_id": user_id, "email": email},
    )


def _write_sync_log(
    admin_engine, client_id: str, config_version: str, result: ReconcileResult
) -> None:
    try:
        with admin_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO `saas_itsm_sync_logs`
                        (`client_id`, `config_version`, `status`,
                         `objects_created`, `objects_updated`, `objects_ignored`,
                         `errors`, `debug_mode`)
                    VALUES
                        (:client_id, :config_version, :status,
                         :created, :updated, :ignored, :errors, 0)
                    """
                ),
                {
                    "client_id": client_id,
                    "config_version": config_version[:50],
                    "status": result.as_status(),
                    "created": result.created,
                    "updated": result.updated,
                    "ignored": result.ignored,
                    "errors": "\n".join(result.errors) or None,
                },
            )
    except Exception:  # pragma: no cover - logging must never break the sync
        pass


def reconcile_client(
    client_id: str,
    snapshot,
    target_engine,
    admin_engine,
    config: dict[str, Any] | None,
    logger,
) -> ReconcileResult:
    """Graft ``snapshot.entities`` under the client root inside ``itsmlocal``."""
    config = config or {}
    config_version = str(
        config.get("config_version") or config.get("sync.config_version") or ""
    )
    result = ReconcileResult()

    # The admin config key can be a bare number (``itsm.0.*``); prefer a readable
    # label for the root entity while keeping ``client_id`` as the mapping scope.
    root_name = (
        str(
            config.get("client_name")
            or config.get("name")
            or config.get("target.entity")
            or client_id
        ).strip()
        or client_id
    )

    source_entities = list(snapshot.entities or [])
    if not source_entities:
        logger.info("Client %s: no source entity to reconcile", client_id)
        _write_sync_log(admin_engine, client_id, config_version, result)
        return result

    with admin_engine.connect() as admin_connection:
        mapping = _load_mapping(admin_connection, client_id)
        user_mapping = _load_user_mapping(admin_connection, client_id)
        profile_mapping = _load_profile_mapping(admin_connection, client_id)

    with target_engine.begin() as connection:
        connection.execute(text("SELECT GET_LOCK(:name, 30)"), {"name": ALLOC_LOCK})
        try:
            writer = _EntityWriter(connection, client_id, config_version, logger)

            # 1. Client root entity, grafted right under the Medulla root.
            #    Scoped under the reserved mapping key ``__client_root__`` so it
            #    never collides with a real source entity id.
            root_map = mapping.get(CLIENT_ROOT_KEY)
            root_local_id = (
                int(root_map["target_glpi_id"])
                if root_map and root_map.get("target_glpi_id")
                else None
            )
            root_completename = f"{MEDULLA_ROOT_NAME}/{root_name}"
            if not root_local_id or not writer.entity_exists(root_local_id):
                root_local_id = writer.find_by_parent_name(MEDULLA_ROOT_ID, root_name)
            if root_local_id is None:
                root_local_id = writer._alloc_id()
                result.created += 1
            writer.upsert_entity(
                root_local_id, root_name, MEDULLA_ROOT_ID, root_completename, 2
            )
            local_by_source: dict[str, int] = {}
            path_by_local: dict[int, tuple[str, int]] = {
                root_local_id: (root_completename, 2)
            }
            pending_mappings: list[tuple[str, str, str, int]] = [
                (CLIENT_ROOT_KEY, "/", root_completename, root_local_id)
            ]

            # 2. Every source entity. The source tree root is grafted too (it
            #    becomes a child of the client root). GLPI ``completename`` uses
            #    a display separator, so order the tree by parent links instead:
            #    keep resolving entities whose parent is already known.
            remaining = list(source_entities)
            while remaining:
                progressed = False
                still_pending = []
                for entity in remaining:
                    source_id = str(entity.get("source_id") or "")
                    if _is_source_root(entity):
                        parent_local_id = root_local_id
                    else:
                        parent_source_id = str(entity.get("source_parent_id") or "0")
                        parent_local_id = local_by_source.get(parent_source_id)
                    if parent_local_id is None:
                        still_pending.append(entity)
                        continue

                    name = str(entity.get("name") or f"entity-{source_id}")
                    parent_completename, parent_level = path_by_local[parent_local_id]
                    completename = f"{parent_completename}/{name}"
                    level = parent_level + 1

                    existing = mapping.get(source_id)
                    local_id = (
                        int(existing["target_glpi_id"])
                        if existing and existing.get("target_glpi_id")
                        else None
                    )
                    is_update = bool(local_id and writer.entity_exists(local_id))
                    if not is_update:
                        local_id = writer.find_by_parent_name(parent_local_id, name)
                        is_update = local_id is not None
                    if local_id is None:
                        local_id = writer._alloc_id()

                    writer.upsert_entity(
                        local_id, name, parent_local_id, completename, level
                    )
                    local_by_source[source_id] = local_id
                    path_by_local[local_id] = (completename, level)
                    pending_mappings.append(
                        (
                            source_id,
                            str(entity.get("path") or name),
                            completename,
                            local_id,
                        )
                    )
                    result.updated += 1 if is_update else 0
                    result.created += 0 if is_update else 1
                    progressed = True

                remaining = still_pending
                if not progressed:
                    for entity in remaining:
                        result.ignored += 1
                        message = (
                            f"entity {entity.get('source_id')} ignored: parent "
                            f"{entity.get('source_parent_id')} not reconciled"
                        )
                        result.errors.append(message)
                        logger.warning("Client %s: %s", client_id, message)
                    break

            # 3. Source users are separate local accounts, scoped by client and
            # source ID. A missing entity mapping rejects the user: it never
            # falls back to the global entity or to the client root.
            profile_names_by_source_id = {
                str(profile.get("source_id") or ""): str(profile.get("name") or "")
                for profile in snapshot.profiles or []
            }
            profile_ids_by_name = _local_profile_ids(connection)
            fallback_profile_id = profile_ids_by_name.get(LOCAL_PROFILE_FALLBACK)
            if fallback_profile_id is None:
                raise RuntimeError("ITSMLocal Self-Service profile is missing")

            scopes_by_user: dict[str, list[dict[str, Any]]] = {}
            for scope in snapshot.user_scopes or []:
                scopes_by_user.setdefault(
                    str(scope.get("source_user_id") or ""), []
                ).append(scope)
            pending_user_mappings: list[tuple[dict[str, Any], int, str]] = []

            for user in snapshot.users or []:
                source_user_id = str(user.get("source_id") or "")
                if not source_user_id:
                    result.ignored += 1
                    result.errors.append("user ignored: missing source id")
                    continue

                default_entity_id = local_by_source.get(
                    str(user.get("default_entity_id") or "")
                )
                if default_entity_id is None:
                    result.ignored += 1
                    message = (
                        f"user {source_user_id} ignored: default entity "
                        f"{user.get('default_entity_id')} is not mapped"
                    )
                    result.errors.append(message)
                    logger.warning("Client %s: %s", client_id, message)
                    continue
                default_profile_name = _local_profile_name(
                    profile_names_by_source_id.get(
                        str(user.get("default_profile_id") or ""), ""
                    ),
                    str(user.get("default_profile_id") or ""),
                    profile_mapping,
                )
                default_profile_id = profile_ids_by_name.get(
                    default_profile_name, fallback_profile_id
                )
                local_login = _local_login(client_id, source_user_id)
                existing_user = user_mapping.get(source_user_id) or {}
                user_id, is_update = _upsert_user(
                    connection,
                    user,
                    local_login,
                    default_entity_id,
                    default_profile_id,
                    existing_user.get("target_user_id"),
                )

                local_scopes: list[dict[str, int]] = []
                seen_scopes: set[tuple[int, int]] = set()
                for scope in scopes_by_user.get(source_user_id, []):
                    entity_id = local_by_source.get(
                        str(scope.get("source_entity_id") or "")
                    )
                    if entity_id is None:
                        result.ignored += 1
                        message = (
                            f"user {source_user_id} scope ignored: entity "
                            f"{scope.get('source_entity_id')} is not mapped"
                        )
                        result.errors.append(message)
                        logger.warning("Client %s: %s", client_id, message)
                        continue
                    profile_name = _local_profile_name(
                        profile_names_by_source_id.get(
                            str(scope.get("source_profile_id") or ""), ""
                        ),
                        str(scope.get("source_profile_id") or ""),
                        profile_mapping,
                    )
                    profile_id = profile_ids_by_name.get(
                        profile_name, fallback_profile_id
                    )
                    scope_key = (profile_id, entity_id)
                    if scope_key in seen_scopes:
                        continue
                    seen_scopes.add(scope_key)
                    local_scopes.append(
                        {
                            "profile_id": profile_id,
                            "entity_id": entity_id,
                            "is_recursive": 1
                            if int(scope.get("is_recursive") or 0)
                            else 0,
                            "is_default": 1 if int(scope.get("is_default") or 0) else 0,
                        }
                    )
                if not local_scopes:
                    local_scopes.append(
                        {
                            "profile_id": default_profile_id,
                            "entity_id": default_entity_id,
                            "is_recursive": 0,
                            "is_default": 1,
                        }
                    )
                _replace_user_scopes(connection, user_id, local_scopes)
                _upsert_user_email(connection, user_id, str(user.get("email") or ""))
                pending_user_mappings.append((user, user_id, local_login))
                result.updated += 1 if is_update else 0
                result.created += 0 if is_update else 1
        finally:
            connection.execute(text("SELECT RELEASE_LOCK(:name)"), {"name": ALLOC_LOCK})

    # 3. Persist the reconciliation mapping in the admin database.
    with admin_engine.begin() as admin_connection:
        for source_id, source_path, target_path, target_glpi_id in pending_mappings:
            _save_mapping(
                admin_connection,
                client_id,
                source_id,
                source_path,
                target_path,
                target_glpi_id,
                config_version,
            )
        for user, target_user_id, target_login in pending_user_mappings:
            _save_user_mapping(
                admin_connection, client_id, user, target_user_id, target_login
            )

    logger.info(
        "Client %s reconciled: %d created, %d updated, %d ignored",
        client_id,
        result.created,
        result.updated,
        result.ignored,
    )
    _write_sync_log(admin_engine, client_id, config_version, result)
    return result
