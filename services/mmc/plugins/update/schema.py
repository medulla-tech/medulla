# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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

from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base; Base = declarative_base()

from mmc.database.database_helper import DBObj

# status global vars
global STATUS_NEUTRAL, STATUS_ENABLED, STATUS_DISABLED
(STATUS_NEUTRAL, STATUS_ENABLED, STATUS_DISABLED) = xrange(3)


class OsClass(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'os_classes'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Update(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'updates'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    uuid = Column(String(255), default = '')
    kb_number = Column(String(255), default = '')
    os_class_id = Column(Integer, ForeignKey('os_classes.id'))
    type_id = Column(Integer, ForeignKey('update_types.id'))
    status = Column(Integer, default = 0)
    need_reboot = Column(Integer, default = 0)
    request_user_input = Column(Integer, default = 0)
    info_url = Column(String(255), default = '')

    # Relations
    update_type = relationship('UpdateType', backref = 'updates')

    os = relationship('OsClass', backref = 'updates')

    targets = relationship('Target', \
        # Auto Defines Target.update field
        backref = 'update', \
        # Delete orphan targets if update is deleted
        cascade = "all, delete-orphan"
    )

class UpdateType(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'update_types'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    status = Column(Integer, default = 0)


class Target(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'targets'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    uuid = Column(Integer)
    update_id = Column(Integer, ForeignKey('updates.id'))
    status = Column(Integer, default = 0)
    is_installed = Column(Integer, default = 0)

