# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/adapters.py

"""ITSM source adapter registry for itsmlocal-sync."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ItsmSnapshot:
    """Common business objects returned by any ITSM adapter."""

    entities: list[dict[str, Any]] = field(default_factory=list)
    users: list[dict[str, Any]] = field(default_factory=list)
    profiles: list[dict[str, Any]] = field(default_factory=list)
    user_scopes: list[dict[str, Any]] = field(default_factory=list)


class ItsmAdapter:
    """Base contract implemented by every ITSM source adapter."""

    adapter_name = "base"

    def __init__(self, client_id: str, config: dict[str, Any], logger):
        self.client_id = client_id
        self.config = config
        self.logger = logger

    def fetch_snapshot(self) -> ItsmSnapshot:
        """Return normalized entities, users, profiles and user scopes."""
        raise NotImplementedError()


_REGISTRY: dict[str, type[ItsmAdapter]] = {}


def register_adapter(adapter_class: type[ItsmAdapter]) -> type[ItsmAdapter]:
    """Register an ITSM adapter class by its adapter_name."""
    _REGISTRY[adapter_class.adapter_name] = adapter_class
    return adapter_class


def get_adapter(adapter_name: str) -> type[ItsmAdapter]:
    """Return an adapter class by name."""
    key = str(adapter_name or "").strip().lower()
    if key not in _REGISTRY:
        raise ValueError(f"unsupported ITSM adapter: {adapter_name}")
    return _REGISTRY[key]


def adapter_names() -> list[str]:
    """Return registered adapter names."""
    return sorted(_REGISTRY.keys())
