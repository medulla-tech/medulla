# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
import datetime

Base = declarative_base()


class AdminDBObj(DBObj):
    # All Admin tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, AdminDBObj):
    # ====== Table name =========================
    __tablename__ = "tests"
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255))


class AdminInventoryEntityRules(Base, AdminDBObj):
    """
    Modèle: table admin_inventory_entity_rules
    
    Objectif: Stocker les règles qui mappent les valeurs TAG aux entités GLPI.
    Permet l'assignation automatique d'entité lors de l'injection d'inventaire.
    
    Algorithme de résolution:
      SELECT entity_id FROM admin_inventory_entity_rules
      WHERE enabled=1 AND tag_name=:tag_name AND tag_value=:tag_value
      ORDER BY priority ASC, id ASC LIMIT 1
    
    Multi-tenancy: Chaque règle mappe une valeur TAG à un entity_id. Plusieurs
    clients peuvent être supportés via différentes valeurs TAG ou noms de règles.
    
    Exemples de règles:
      tag_value="PROD" → entity_id=1 (Siège)
      tag_value="FILIALE" → entity_id=2 (Filiale)
      tag_value="CLIENT-A" → entity_id=3 (Client A)
    """
    
    __tablename__ = "admin_inventory_entity_rules"
    
    enabled = Column(TINYINT(1), nullable=False, default=1)
    rule_name = Column(String(190), nullable=False)
    tag_name = Column(String(100), nullable=False)
    tag_value = Column(String(255), nullable=False)
    entity_id = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False, default=100)
    stop_on_match = Column(TINYINT(1), nullable=False, default=1)
    comment = Column(String(255))
    created_by = Column(String(100))
    updated_by = Column(String(100))
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("tag_name", "tag_value", "priority", name="uniq_tag_rule"),
    )
    
    def __repr__(self):
        return f"<AdminInventoryEntityRules(id={self.id}, tag_value={self.tag_value}, entity_id={self.entity_id})>"


class SubstituteInventoryMetadata(Base, AdminDBObj):
    """
    Modèle: table substitute_inventory_metadata
    
    Objectif: Stocker des métadonnées key/value personnalisées associées à chaque machine.
    Permet l'extension des données d'inventaire sans modifier le schéma principal.
    
    Identification de la machine: Format JID (ex: "laptop-001@medulla.local")
    Le JID est extrait de l'inventaire selon la chaîne de priorité:
      1. ACCOUNTINFO/NAME ou META/NAME
      2. HARDWARE/DEVICEID
      3. UUID généré si aucun des deux disponibles
    
    Pattern UPSERT: (jid, key_name) est unique; les mises à jour utilisent INSERT ... ON DUPLICATE KEY UPDATE
    avec mise à jour de updated_at uniquement si la valeur change.
    
    Exemples de paires de métadonnées:
      jid="laptop-001@medulla.local" + key="department" + value="IT-PROD"
      jid="laptop-001@medulla.local" + key="cost_center" + value="CC-12345"
      jid="laptop-001@medulla.local" + key="last_deploy" + value="2026-07-13 10:30:00"
    
    Une machine peut avoir un nombre illimité de paires de métadonnées.
    """
    
    __tablename__ = "substitute_inventory_metadata"
    
    jid = Column(String(255), nullable=False)
    hostname = Column(String(255), nullable=False, default="")
    key_name = Column(String(255), nullable=False)
    value = Column(Text)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("jid", "key_name", name="uniq_jid_key"),
    )
    
    def __repr__(self):
        value_display = (self.value[:50] + "...") if self.value and len(self.value) > 50 else self.value
        return (
            f"<SubstituteInventoryMetadata(jid={self.jid}, hostname={self.hostname}, "
            f"key_name={self.key_name}, value={value_display})>"
        )
