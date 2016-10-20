# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()


class XmppMasterDBObj(DBObj):
    # All XmppMaster tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class UserLog(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'userlog'
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    msg = Column(String(255), nullable=False)
    datelog =  Column(DateTime, default=datetime.datetime.utcnow)
    type =  Column(String(10), nullable=False,default = "info")

class Machines(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'machines'
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    jid = Column(String(45), nullable=False)
    platform = Column(String(60))
    hostname = Column(String(45), nullable=False)
    archi= Column(String(45), nullable=False)
    uuid_inventorymachine= Column(String(45), nullable=False)
    ip_xmpp = Column(String(45))
    subnetxmpp = Column(String(45))
    macaddress = Column(String(45))
    agenttype= Column(String(20))
    classutil = Column(String(20))
    urlguacamole =Column(String(255))
    groupdeploy = Column(String(80))


class Network(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'network'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    macaddress = Column(String(45), nullable=False)
    ipaddress = Column(String(45), nullable=False)
    broadcast = Column(String(45))
    gateway = Column(String(45))
    mask = Column(String(45))
    mac = Column(String(45), nullable=False)
    # ====== ForeignKey =============================
    #machines_id = Column(Integer, nullable=False)
    machines_id = Column(Integer, ForeignKey('machines.id'))
    machines = relationship(Machines)


class RelayServer(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'relayserver'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    urlguacamole =Column(String(80))
    subnet = Column(String(45))
    nameserver = Column(String(45))
    groupdeploy = Column(String(45))
    ipserver = Column(String(45))
    port = Column(Integer)
    ipconnection = Column(String(45))
    portconnection = Column(Integer)
    mask = Column(String(45))
    jid = Column(String(45))
    longitude = Column(String(45))
    latitude = Column(String(45))
    enabled=  Column(Boolean, unique=False)
    classutil = Column(String(10))

class Regles(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'rules'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    name =Column(String(45))
    description = Column(String(45))
    level = Column(Integer)

class Users(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'users'
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    namesession = Column(String(45))
    hostname = Column(String(45))
    city = Column(String(45))
    region_name = Column(String(45))
    time_zone = Column(String(45))
    longitude = Column(String(45))
    latitude = Column(String(45))
    postal_code = Column(String(45))
    country_code = Column(String(45))
    country_name = Column(String(45))

class Has_machinesusers(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'has_machinesusers'
    # ====== ForeignKey =============================
    machines_id = Column(Integer, ForeignKey('machines.id'))
    users_id = Column(Integer, ForeignKey('users.id'))
    machines = relationship(Machines)
    users = relationship(Users)

class Has_relayserverrules(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'has_relayserverrules'
    # ====== ForeignKey =============================
    rules_id = Column(Integer, ForeignKey('rules.id'))
    relayserver_id = Column(Integer)
    subject = Column(String(45))
    order = Column(String(45))
    rules = relationship(Regles)

class Has_guacamole(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'has_guacamole'
    # ====== ForeignKey =============================
    idguacamole = Column(Integer)
    idinventory = Column(Integer)
    protocol   = Column(String(10))

class Version(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'version'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    active = Column(TINYINT(1), nullable=False, default=1)