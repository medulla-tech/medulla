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

from sqlalchemy import Column, String, Integer,  ForeignKey
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship

Base = declarative_base()


class XmppMasterDBObj(DBObj):
    # All XmppMaster tables have id colmun as primary key
    id = Column(Integer, primary_key=True)

class Machines(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'machines'
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    jid = Column(String(45), nullable=False)
    plateform = Column(String(60))
    hostname = Column(String(45), nullable=False)
    archi= Column(String(45), nullable=False)
    uuid_inventorymachine= Column(String(45), nullable=False)
    ip_xmpp = Column(String(45))
    subnetxmpp = Column(String(45))
    macadress = Column(String(45))
    agenttype= Column(String(20))

class Network(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'network'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    macadress = Column(String(45), nullable=False)
    ipadress = Column(String(45), nullable=False)
    broadcast = Column(String(45))
    gateway = Column(String(45))
    mask = Column(String(45))
    mac = Column(String(45), nullable=False)
    # ====== ForeignKey =============================
    #machines_id = Column(Integer, nullable=False)
    machines_id = Column(Integer, ForeignKey('machines.id'))
    machines = relationship(Machines)


class RelaisServer(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'relaisserver'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    urlguacamole =Column(String(80))
    subnet = Column(String(45))
    nameserver = Column(String(45))
    ipserver = Column(String(45))
    mask = Column(String(45))
    jid = Column(String(45))
    

class Version(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'version'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    active = Column(TINYINT(1), nullable=False, default=1)