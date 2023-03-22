# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from sqlalchemy import Column, String, Text, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj


Base = declarative_base()


class BackupPCDBObj(DBObj):
    # All BackupPC tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Backup_profiles(Base, BackupPCDBObj):
    # ====== Table name =========================
    __tablename__ = 'backup_profiles'
    # ====== Fields =============================
    profilename = Column(String(255))
    sharenames = Column(Text())
    excludes = Column(Text())
    encoding = Column(String(50))


class Period_profiles(Base, BackupPCDBObj):
    # ====== Table name =========================
    __tablename__ = 'period_profiles'
    # ====== Fields =============================
    profilename = Column(String(255))
    full = Column(Float())
    incr = Column(Float())
    exclude_periods = Column(Text())


class Backup_servers(Base, BackupPCDBObj):
   # ====== Table name =========================
    __tablename__ = 'backup_servers'
    # ====== Fields =============================
    entity_uuid = Column(String(50))
    backupserver_url = Column(String(255))


class Hosts(Base, BackupPCDBObj):
    # ====== Table name =========================
    __tablename__ = 'hosts'
    # ====== Fields =============================
    uuid = Column(String(50))
    backup_profile = Column(Integer)
    period_profile = Column(Integer)
    pre_backup_script = Column(Text, default='')
    post_backup_script = Column(Text, default='')
    pre_restore_script = Column(Text, default='')
    post_restore_script = Column(Text, default='')
    reverse_port = Column(Integer)
