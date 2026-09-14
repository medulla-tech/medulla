# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
SQLAlchemy mapping of the reflex database.

The tables are created by services/contrib/reflex/sql/schema-001.sql, not by
this module: the mapping only describes what the schema already defines. Any
change here without the matching SQL script is a divergence.
"""

from sqlalchemy.dialects import mysql
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Text,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from mmc.database.database_helper import DBObj
import datetime

Base = declarative_base()

SEVERITIES = ('info', 'medium', 'high', 'critical')
OPERATORS = ('gt', 'gte', 'lt', 'lte', 'eq', 'ne',
             'between', 'outside', 'changed')
OPERATING_SYSTEMS = ('windows', 'linux', 'darwin')
VISIBILITIES = ('private', 'entity', 'global')
# What a user may choose for a probe of his own.
USER_VISIBILITIES = ('private', 'entity')
CATEGORIES = ('system', 'security', 'network', 'storage', 'service', 'application')
VALUE_TYPES = ('numeric', 'text', 'boolean')
TARGET_TYPES = ('machine', 'group', 'entity')
MEASURE_STATUSES = ('ok', 'warning', 'error', 'unavailable')
ALERT_STATUSES = ('open', 'ack', 'resolved')
CHANNEL_TYPES = ('email', 'telegram', 'webhook', 'slack', 'teams', 'sms', 'whatsapp')
NOTIFICATION_STATUSES = ('pending', 'sent', 'failed', 'skipped')


class ReflexDBObj(DBObj):
    """Base class for Reflex module DB objects"""
    pass


class Probe(Base, ReflexDBObj):
    """Probe definition: what is measured."""
    __tablename__ = 'probes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_key = Column(String(128), nullable=False, unique=True)
    label = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(64), nullable=False, default='system')
    probe_type = Column(Enum('builtin', 'script'), nullable=False, default='builtin')
    metric_key = Column(String(128), nullable=False)
    unit = Column(String(32))
    value_type = Column(Enum(*VALUE_TYPES), nullable=False, default='numeric')
    # 1 = the machine sheet draws the curve of the measures of this probe.
    plottable = Column(Integer, nullable=False, default=1)
    # MySQL SET column, handled as a comma separated string.
    os_support = Column(String(64), nullable=False, default='windows,linux')
    min_interval_seconds = Column(Integer, nullable=False, default=300)
    default_interval_seconds = Column(Integer, nullable=False, default=300)
    is_builtin = Column(Integer, nullable=False, default=0)
    visibility = Column(Enum(*VISIBILITIES), nullable=False, default='entity')
    # Entity the probe is scoped to when visibility = 'entity'.
    entity_id = Column(String(255))
    owner_login = Column(String(255))
    enabled = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now,
                        onupdate=datetime.datetime.now)

    conditions = relationship("ProbeCondition", back_populates="probe",
                              cascade="all, delete-orphan")
    collectors = relationship("ProbeCollector", back_populates="probe",
                              cascade="all, delete-orphan")
    assignments = relationship("ProbeAssignment", back_populates="probe",
                               cascade="all, delete-orphan")
    exclusions = relationship("ProbeExclusion", back_populates="probe",
                              cascade="all, delete-orphan")


class ProbeCondition(Base, ReflexDBObj):
    """Alert condition attached to a probe: when to raise."""
    __tablename__ = 'probe_conditions'
    __table_args__ = (
        UniqueConstraint('probe_id', 'display_order', name='uk_probe_order'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'),
                      nullable=False)
    operator = Column(Enum(*OPERATORS), nullable=False)

    # What the product ships, or the definition of the owner for a personal
    # probe.
    default_threshold_value = Column(Float)
    default_threshold_value2 = Column(Float)
    default_threshold_text = Column(String(255))
    default_duration_seconds = Column(Integer, nullable=False, default=0)
    default_severity = Column(Enum(*SEVERITIES), nullable=False, default='medium')
    default_message_template = Column(String(512))
    default_enabled = Column(Integer, nullable=False, default=1)

    # What the operator chose, NULL as long as he chose nothing.
    threshold_value = Column(Float)
    threshold_value2 = Column(Float)
    threshold_text = Column(String(255))
    duration_seconds = Column(Integer)
    severity = Column(Enum(*SEVERITIES))
    message_template = Column(String(512))
    enabled = Column(Integer)

    # So that support knows a threshold is no longer the one of the product.
    customized_by = Column(String(255))
    customized_at = Column(DateTime)
    display_order = Column(Integer, nullable=False, default=0)

    probe = relationship("Probe", back_populates="conditions")


class ProbeConditionOverride(Base, ReflexDBObj):
    """What one estate chose for one condition."""
    __tablename__ = 'probe_condition_overrides'
    __table_args__ = (
        UniqueConstraint('condition_id', 'entity_id', name='uk_condition_entity'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    condition_id = Column(Integer,
                          ForeignKey('probe_conditions.id', ondelete='CASCADE'),
                          nullable=False)
    # The bare GLPI identifier, as probes.entity_id spells it.
    entity_id = Column(String(255), nullable=False)

    threshold_value = Column(Float)
    threshold_value2 = Column(Float)
    threshold_text = Column(String(255))
    duration_seconds = Column(Integer)
    severity = Column(Enum(*SEVERITIES))
    message_template = Column(String(512))
    enabled = Column(Integer)

    customized_by = Column(String(255), nullable=False)
    customized_at = Column(DateTime, nullable=False,
                           default=datetime.datetime.now)


class ProbeCollector(Base, ReflexDBObj):
    """How a probe is measured, per operating system."""
    __tablename__ = 'probe_collectors'
    __table_args__ = (
        UniqueConstraint('probe_id', 'os', name='uk_probe_os'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'),
                      nullable=False)
    os = Column(Enum(*OPERATING_SYSTEMS), nullable=False)
    collector = Column(String(128), nullable=False)
    params_json = Column(Text)
    implementation_note = Column(String(512))
    requires = Column(String(255))
    enabled = Column(Integer, nullable=False, default=1)

    probe = relationship("Probe", back_populates="collectors")


class ProbeAssignment(Base, ReflexDBObj):
    """Where a probe is placed and at which cadence."""
    __tablename__ = 'probe_assignments'
    __table_args__ = (
        UniqueConstraint('probe_id', 'target_type', 'target_id',
                         name='uk_probe_target'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'),
                      nullable=False)
    target_type = Column(Enum(*TARGET_TYPES), nullable=False)
    target_id = Column(String(255), nullable=False)
    interval_seconds = Column(Integer, nullable=False, default=300)
    created_by = Column(String(255), nullable=False)
    language = Column(String(5))
    created_at = Column(DateTime, default=datetime.datetime.now)

    probe = relationship("Probe", back_populates="assignments")


class ProbeExclusion(Base, ReflexDBObj):
    """Exception to a widely placed probe, machine by machine."""
    __tablename__ = 'probe_exclusions'
    __table_args__ = (
        UniqueConstraint('probe_id', 'machines_id', name='uk_probe_machine'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'),
                      nullable=False)
    machines_id = Column(Integer, nullable=False)
    hostname = Column(String(255), nullable=False)
    reason = Column(String(255))
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    probe = relationship("Probe", back_populates="exclusions")


class ProbeAgentConfig(Base, ReflexDBObj):
    """Probe configuration distributed to an agent."""
    __tablename__ = 'probe_agent_config'
    __table_args__ = (
        UniqueConstraint('machines_id', name='uk_machine'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    machines_id = Column(Integer, nullable=False)
    hostname = Column(String(255), nullable=False)
    sent_version = Column(String(64))
    sent_at = Column(DateTime)
    acked_version = Column(String(64))
    acked_at = Column(DateTime)
    probe_count = Column(Integer, nullable=False, default=0)
    last_error = Column(String(512))
    updated_at = Column(DateTime, default=datetime.datetime.now,
                        onupdate=datetime.datetime.now)


CONFIG_CHANGE_SCOPES = ('machine', 'group', 'entity', 'all', 'probe')


class ProbeConfigChange(Base, ReflexDBObj):
    """Queue of the gestures that change what a machine has to measure."""
    __tablename__ = 'probe_config_changes'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    scope_type = Column(Enum(*CONFIG_CHANGE_SCOPES), nullable=False)
    scope_id = Column(Integer)
    created_at = Column(DateTime, nullable=False,
                        default=datetime.datetime.now)


class ProbeMeasure(Base, ReflexDBObj):
    """Measures reported by the agents."""
    __tablename__ = 'probe_measures'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    machines_id = Column(Integer, nullable=False)
    uuid_inventorymachine = Column(String(45))
    hostname = Column(String(255), nullable=False)
    probe_id = Column(Integer, nullable=False)
    metric_key = Column(String(128), nullable=False)
    value_num = Column(Float)
    value_text = Column(String(512))
    unit = Column(String(32))
    status = Column(Enum(*MEASURE_STATUSES), nullable=False, default='ok')
    detail = Column(String(512))
    # Millisecond precision: a condition duration is judged on the gap between
    # two measures, and a truncation to the second decides the alert.
    collected_at = Column(mysql.DATETIME(fsp=3), nullable=False)
    received_at = Column(mysql.TIMESTAMP(fsp=3))


class Alert(Base, ReflexDBObj):
    """Alert raised by a condition."""
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'),
                      nullable=False)
    condition_id = Column(Integer)
    machines_id = Column(Integer, nullable=False)
    uuid_inventorymachine = Column(String(45))
    hostname = Column(String(255), nullable=False)
    severity = Column(Enum(*SEVERITIES), nullable=False)
    status = Column(Enum(*ALERT_STATUSES), nullable=False, default='open')
    value_at_trigger = Column(Float)
    value_text_at_trigger = Column(String(512))
    # Copy of the triggering measure detail, frozen when the alert opened.
    detail_at_trigger = Column(String(512))
    message = Column(String(512), nullable=False)
    opened_at = Column(DateTime, default=datetime.datetime.now)
    last_seen_at = Column(DateTime, default=datetime.datetime.now)
    occurrence_count = Column(Integer, nullable=False, default=1)
    ack_user = Column(String(255))
    ack_at = Column(DateTime)
    ack_comment = Column(String(512))
    resolved_at = Column(DateTime)


class NotificationChannel(Base, ReflexDBObj):
    """Notification channel."""
    __tablename__ = 'notification_channels'
    __table_args__ = (
        UniqueConstraint('entity_id', 'name', name='uk_entity_name'),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    # Entity owning the channel, a bare GLPI entity id.
    entity_id = Column(String(255), nullable=False)
    channel_type = Column(Enum(*CHANNEL_TYPES), nullable=False, default='email')
    config_json = Column(Text)
    secret_encrypted = Column(Text)
    enabled = Column(Integer, nullable=False, default=1)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now,
                        onupdate=datetime.datetime.now)

    rules = relationship("NotificationRule", back_populates="channel",
                         cascade="all, delete-orphan")


class NotificationRule(Base, ReflexDBObj):
    """Who receives what."""
    __tablename__ = 'notification_rules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer,
                        ForeignKey('notification_channels.id', ondelete='CASCADE'),
                        nullable=False)
    probe_id = Column(Integer, ForeignKey('probes.id', ondelete='CASCADE'))
    min_severity = Column(Enum(*SEVERITIES), nullable=False, default='high')
    recipients = Column(Text)
    target_filter = Column(String(255))
    cooldown_minutes = Column(Integer, nullable=False, default=60)
    escalation_minutes = Column(Integer)
    enabled = Column(Integer, nullable=False, default=1)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    channel = relationship("NotificationChannel", back_populates="rules")


class NotificationHistory(Base, ReflexDBObj):
    """Trace of the sendings, and support of the anti repetition."""
    __tablename__ = 'notification_history'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(Integer)
    channel_id = Column(Integer)
    rule_id = Column(Integer)
    recipients = Column(Text)
    status = Column(Enum(*NOTIFICATION_STATUSES), nullable=False, default='pending')
    skip_reason = Column(String(255))
    error_message = Column(String(512))
    attempt_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime)
    accepted_at = Column(DateTime)
    provider_message_id = Column(String(255))
    is_escalation = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)
    sent_at = Column(DateTime)


class Setting(Base, ReflexDBObj):
    """Operating settings of the module, editable from the console."""
    __tablename__ = 'settings'
    setting_key = Column(String(128), primary_key=True)
    default_value = Column(String(512), nullable=False)
    value = Column(String(512))
    value_type = Column(Enum('int', 'bool', 'string'), nullable=False,
                        default='string')
    exposed = Column(Integer, nullable=False, default=1)
    updated_by = Column(String(255))
    updated_at = Column(DateTime, default=datetime.datetime.now)


class Version(Base, ReflexDBObj):
    """Schema version, written by the SQL scripts."""
    __tablename__ = 'version'
    Number = Column(Integer, primary_key=True)
