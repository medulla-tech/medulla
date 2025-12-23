# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text, Enum, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class StoreDBObj(DBObj):
    id = Column(Integer, primary_key=True)

class Software(Base, StoreDBObj):
    __tablename__ = 'software'

    name = Column(String(255), nullable=False)
    vendor = Column(String(100))
    description = Column(Text)
    short_desc = Column(String(100))
    website = Column(String(255))
    track = Column(String(50), nullable=False)
    os = Column(String(20), nullable=False)
    arch = Column(String(20))
    languages = Column(String(255), nullable=False)
    is_multilingual = Column(TINYINT, default=0)
    version = Column(String(50))
    version_api_url = Column(String(500))
    download_url = Column(String(500))
    download_path = Column(String(500))
    uninstall_cmd = Column(String(500))
    launch_cmd = Column(String(500))
    last_check = Column(DateTime)
    last_update = Column(DateTime)
    active = Column(TINYINT, default=1)
    popularity_score = Column(Integer, default=0)
    subscribers_count = Column(Integer, default=0)
    popularity_updated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    downloads = relationship("SoftwareDownload", back_populates="software")

class SoftwareDownload(Base, StoreDBObj):
    __tablename__ = 'software_downloads'

    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)
    version = Column(String(50), nullable=False)
    lang = Column(String(10), nullable=False)
    status = Column(Enum('success', 'failed', 'pending'), default='pending')
    error_message = Column(Text)
    download_path = Column(String(500))
    filename = Column(String(255))
    file_size_mb = Column(Integer)
    sha256 = Column(String(64))
    package_uuid = Column(String(36))
    medulla_path = Column(String(500))
    package_built_at = Column(DateTime)
    deployed_at = Column(DateTime)
    downloaded_at = Column(DateTime, nullable=False)

    software = relationship("Software", back_populates="downloads")

class SoftwareRequest(Base, StoreDBObj):
    __tablename__ = 'software_requests'

    software_name = Column(String(255), nullable=False)
    os = Column(String(20))
    message = Column(Text)
    requester_name = Column(String(100), nullable=False)
    requester_email = Column(String(255), nullable=False)
    status = Column(Enum('pending', 'approved', 'rejected', 'completed'), default='pending')
    admin_notes = Column(Text)
    ai_status = Column(Enum('pending', 'processing', 'completed', 'failed', 'skipped'), default='pending')
    ai_suggestions = Column(LONGTEXT)
    ai_confidence = Column(DECIMAL(3, 2))
    ai_error = Column(Text)
    ai_processed_at = Column(DateTime)
    software_id = Column(Integer, ForeignKey('software.id'))
    created_at = Column(DateTime, default=datetime.datetime.now)
    processed_at = Column(DateTime)

class Version(Base, StoreDBObj):
    __tablename__ = 'version'
    id = Column(Integer, primary_key=True, autoincrement=False)
    Number = Column(TINYINT, default=0)

class Client(Base, StoreDBObj):
    __tablename__ = 'clients'

    uuid = Column(String(36), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    server_key = Column(String(50), nullable=False, unique=True)
    contact_email = Column(String(255))
    active = Column(TINYINT, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    subscriptions = relationship("Subscription", back_populates="client")

class Subscription(Base, StoreDBObj):
    __tablename__ = 'subscriptions'

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    software_id = Column(Integer, ForeignKey('software.id'), nullable=False)
    subscribed_at = Column(DateTime, default=datetime.datetime.now)

    client = relationship("Client", back_populates="subscriptions")
    software = relationship("Software")
