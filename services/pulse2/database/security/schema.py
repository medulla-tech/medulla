# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Column, String, Integer, Text, DateTime, Date, Enum, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from mmc.database.database_helper import DBObj
import datetime

Base = declarative_base()


class SecurityDBObj(DBObj):
    """Base class for Security module DB objects"""
    pass


class Tests(Base, SecurityDBObj):
    """Test table (for module activation test)"""
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    message = Column(String(255))


class Cve(Base, SecurityDBObj):
    """Cache local des CVEs récupérées de CVE Central"""
    __tablename__ = 'cves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cve_id = Column(String(20), nullable=False, unique=True)
    cvss_score = Column(DECIMAL(3, 1))
    severity = Column(Enum('Critical', 'High', 'Medium', 'Low', 'None', 'N/A'), default='N/A')
    description = Column(Text)
    published_at = Column(Date)
    last_modified = Column(Date)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relations
    software_cves = relationship("SoftwareCve", back_populates="cve", cascade="all, delete-orphan")


class SoftwareCve(Base, SecurityDBObj):
    """Lien entre logiciels et CVEs"""
    __tablename__ = 'software_cves'
    id = Column(Integer, primary_key=True, autoincrement=True)
    software_name = Column(String(255), nullable=False)  # Nom normalisé (ex: "Python")
    software_version = Column(String(100), nullable=False)  # Version normalisée (ex: "3.11.9")
    glpi_software_name = Column(String(255), nullable=True)  # Nom original GLPI pour jointure
    target_platform = Column(String(50), nullable=True)  # Platform cible du CPE (android, macos, ios, windows, etc.)
    cve_id = Column(Integer, ForeignKey('cves.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relations
    cve = relationship("Cve", back_populates="software_cves")


class Scan(Base, SecurityDBObj):
    """Historique des scans"""
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(Enum('running', 'completed', 'failed'), default='running')
    softwares_sent = Column(Integer, default=0)
    cves_received = Column(Integer, default=0)
    machines_affected = Column(Integer, default=0)
    error_message = Column(Text)


class CveExclusion(Base, SecurityDBObj):
    """CVE à ignorer"""
    __tablename__ = 'cve_exclusions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cve_id = Column(String(20), nullable=False, unique=True)
    reason = Column(Text)
    excluded_by = Column(String(100))
    excluded_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)



# NOTE: Configuration is now read from /etc/mmc/plugins/security.ini and security.ini.local
# The scan_config table has been removed - config is managed via ini files like other modules
