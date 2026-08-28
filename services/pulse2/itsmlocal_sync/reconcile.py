# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/reconcile.py

"""Reconcile an ITSM snapshot into the itsmlocal target database.

For each client, Medulla owns a dedicated root entity in ``itsmlocal`` and
grafts the client organisation (entities) underneath it. The source ids are
never reused locally: every source entity gets a stable local id, recorded in
``admin.saas_itsm_entity_mapping`` (unique on ``client_id`` + ``source_id``).

Only entities are handled here; users and profiles are a later step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import text

MEDULLA_ROOT_ID = 0
MEDULLA_ROOT_NAME = "Medulla"
ALLOC_LOCK = "itsmlocal_entity_alloc"


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


def _path_segments(path: str) -> list[str]:
    return [segment for segment in str(path or "").split("/") if segment]


def _sorted_by_depth(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order entities so a parent is always processed before its children."""
    return sorted(entities, key=lambda row: len(_path_segments(row.get("path"))))


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
    config_version = str(config.get("config_version") or config.get("sync.config_version") or "")
    result = ReconcileResult()

    source_entities = list(snapshot.entities or [])
    if not source_entities:
        logger.info("Client %s: no source entity to reconcile", client_id)
        _write_sync_log(admin_engine, client_id, config_version, result)
        return result

    with admin_engine.connect() as admin_connection:
        mapping = _load_mapping(admin_connection, client_id)

    with target_engine.begin() as connection:
        connection.execute(
            text("SELECT GET_LOCK(:name, 30)"), {"name": ALLOC_LOCK}
        )
        try:
            writer = _EntityWriter(connection, client_id, config_version, logger)

            # 1. Client root entity, grafted right under the Medulla root.
            root_map = mapping.get("0")
            root_local_id = (
                int(root_map["target_glpi_id"])
                if root_map and root_map.get("target_glpi_id")
                else None
            )
            root_completename = f"{MEDULLA_ROOT_NAME}/{client_id}"
            if not root_local_id or not writer.entity_exists(root_local_id):
                root_local_id = writer.find_by_parent_name(MEDULLA_ROOT_ID, client_id)
            if root_local_id is None:
                root_local_id = writer._alloc_id()
                result.created += 1
            writer.upsert_entity(
                root_local_id, client_id, MEDULLA_ROOT_ID, root_completename, 2
            )
            local_by_source: dict[str, int] = {"0": root_local_id}
            path_by_local: dict[int, tuple[str, int]] = {
                root_local_id: (root_completename, 2)
            }
            pending_mappings: list[tuple[str, str, str, int]] = [
                ("0", "/", root_completename, root_local_id)
            ]

            # 2. Every source sub-entity, parents first.
            for entity in _sorted_by_depth(source_entities):
                source_id = str(entity.get("source_id") or "")
                if _is_source_root(entity):
                    continue

                parent_source_id = str(entity.get("source_parent_id") or "0")
                parent_local_id = local_by_source.get(parent_source_id)
                if parent_local_id is None:
                    result.ignored += 1
                    message = (
                        f"entity {source_id} ignored: parent {parent_source_id} "
                        f"not reconciled"
                    )
                    result.errors.append(message)
                    logger.warning("Client %s: %s", client_id, message)
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
                    (source_id, str(entity.get("path") or name), completename, local_id)
                )

                if is_update:
                    result.updated += 1
                else:
                    result.created += 1
        finally:
            connection.execute(
                text("SELECT RELEASE_LOCK(:name)"), {"name": ALLOC_LOCK}
            )

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

    logger.info(
        "Client %s reconciled: %d created, %d updated, %d ignored",
        client_id,
        result.created,
        result.updated,
        result.ignored,
    )
    _write_sync_log(admin_engine, client_id, config_version, result)
    return result
