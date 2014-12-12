# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

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
    pre_backup_script = Column(Text)
    post_backup_script = Column(Text)
    pre_restore_script = Column(Text)
    post_restore_script = Column(Text)
