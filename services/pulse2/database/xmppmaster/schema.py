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

from sqlalchemy import Column, String, Integer, Boolean, \
    ForeignKey, DateTime, Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()


class XmppMasterDBObj(DBObj):
    # All XmppMaster tables have id colmun as primary key
    id = Column(Integer, primary_key=True)

class Qa_custom_command(Base):
    ## ====== Table name =========================
    __tablename__ = 'qa_custom_command'
    ## ====== Fields =============================
    namecmd = Column(String(45), primary_key=True)
    user =  Column(String(45), primary_key=True)
    os = Column(String(45), primary_key=True)
    customcmd = Column(Text, nullable=False)
    description = Column(String(45), nullable=False, default = "")

class Logs(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'logs'
    # ====== Fields =============================
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    type = Column(String(6), nullable=False,default = "noset")
    date = Column(DateTime, default=datetime.datetime.now)
    text = Column(Text, nullable=False)
    sessionname = Column(String(20), nullable=False, default = "")
    priority = Column(Integer, default = 0)
    who = Column(String(45), nullable=False, default = "")
    how = Column(String(255), nullable=False, default = "")
    why = Column(String(255), nullable=False, default = "")
    module = Column(String(45), nullable=False, default = "")
    action = Column(String(45), nullable=False, default = "")
    touser = Column(String(45), nullable=False, default = "")
    fromuser = Column(String(45), nullable=False, default = "")

class UserLog(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'userlog'
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    msg = Column(String(255), nullable=False)
    datelog =  Column(DateTime, default=datetime.datetime.now)
    type =  Column(String(10), nullable=False,default = "info")

################################
class Syncthingsync(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'syncthingsync'
    # ====== Fields =============================
    # Here we define columns for the table syncthingsync.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    uuidpackage = Column(String(40), nullable=False)
    typesynchro =  Column(String(10), nullable=False, default = "create")
    relayserver_jid = Column(String(255))
    watching =  Column(String(3), nullable=False, default = "yes")
    date = Column(DateTime, default=datetime.datetime.utcnow)

##########DEPLOY PAR SYNCTHING######################
class Syncthing_deploy_group(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'syncthing_deploy_group'
    # ====== Fields =============================
    # Here we define columns for the table syncthing_deploy_group.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    namepartage = Column(String(80), nullable=False)
    directory_tmp = Column(String(80), nullable=False)
    dateend = Column(DateTime, default=datetime.datetime.now)
    package= Column(String(90), nullable=False)
    status = Column(String(6), nullable=False)
    grp_parent = Column(Integer, nullable=False)
    cmd = Column(Integer, nullable=False)
    nbtransfert = Column(Integer, nullable=False, default = 0)

class Syncthing_ars_cluster(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'syncthing_ars_cluster'
    # ====== Fields =============================
    # Here we define columns for the table syncthing_ars_cluster.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    numcluster = Column(Integer, nullable=False)
    namecluster       = Column(String(45))
    liststrcluster    = Column(Text , nullable=False)
    arsmastercluster       = Column(String(255), nullable=False)
    devivesyncthing       = Column(String(512), nullable=False)
    keypartage = Column(String(255))
    type_partage = Column(String(45))
    # ====== ForeignKey =============================
    #machines_id = Column(Integer, nullable=False)
    fk_deploy = Column(Integer, ForeignKey('syncthing_deploy_group.id'), nullable=False)
    syncthing_deploy_group = relationship(Syncthing_deploy_group)

class Syncthing_machine(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'syncthing_machine'
    # ====== Fields =============================
    # Here we define columns for the table syncthing_machine.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    jidmachine      = Column(String(255), nullable=False)
    inventoryuuid   = Column(String(45), nullable=False)
    title           = Column(String(255))
    jid_relay       = Column(String(255), nullable=False)
    cluster         = Column(String(1024), nullable=False)
    pathpackage     = Column(String(100), nullable=False)
    state           = Column(String(45), nullable=False)
    sessionid       = Column(String(45), nullable=False)
    start           = Column(DateTime, nullable=False)
    startcmd        = Column(DateTime, nullable=False)
    endcmd          = Column(DateTime, nullable=False)
    user            = Column(String(45), nullable=False)
    command         = Column(Integer, nullable=False)
    group_uuid      = Column(Integer, nullable=False)
    login           = Column(String(45))
    macadress       = Column(String(255))
    syncthing       = Column(Integer, nullable=False)
    result          = Column(Text , nullable=False)
    comment         = Column(String(255))
    progress        = Column(Integer, nullable=False, default = 0)
    fk_arscluster   = Column(Integer, ForeignKey('syncthing_ars_cluster.id'), nullable=False)
    syncthing_ars_cluster = relationship(Syncthing_ars_cluster)

class Machines(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'machines'
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    jid = Column(String(255), nullable=False)
    enabled=  Column(Boolean, unique=False)
    platform = Column(String(60))
    hostname = Column(String(45), nullable=False)
    archi= Column(String(45), nullable=False)
    uuid_inventorymachine= Column(String(45), nullable=False)
    ippublic = Column(String(20))
    ip_xmpp = Column(String(45))
    subnetxmpp = Column(String(45))
    macaddress = Column(String(45))
    agenttype= Column(String(20))
    classutil = Column(String(20))
    urlguacamole =Column(String(255))
    groupdeploy = Column(String(80))
    picklekeypublic = Column(String(550))
    ad_ou_machine = Column(Text)
    ad_ou_user = Column(Text)
    kiosk_presence = Column(Enum('False', 'True'))
    lastuser = Column(String(45))
    keysyncthing = Column(String(70), default="")

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
    urlguacamole =Column(String(255))
    subnet = Column(String(45))
    nameserver = Column(String(45))
    groupdeploy = Column(String(45))
    package_server_ip = Column(String(45))
    package_server_port = Column(Integer)
    ipserver = Column(String(45))
    port = Column(Integer)
    ipconnection = Column(String(45))
    portconnection = Column(Integer)
    mask = Column(String(45))
    jid = Column(String(255))
    longitude = Column(String(45))
    latitude = Column(String(45))
    enabled=  Column(Boolean, unique=False)
    classutil = Column(String(10))
    moderelayserver = Column(String(7))
    keysyncthing = Column(String(70), default="")

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

class Has_cluster_ars(Base, XmppMasterDBObj):
    ## ====== Table name =========================
    __tablename__ = 'has_cluster_ars'
    ## ====== ForeignKey =============================
    id_ars = Column(Integer)
    id_cluster = Column(Integer)

class Cluster_ars(Base, XmppMasterDBObj):
    ## ====== Table name =========================
    __tablename__ = 'cluster_ars'
    ## ====== ForeignKey =============================
    name = Column(String(40))
    description = Column(String(255))

class Version(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'version'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    active = Column(TINYINT(1), nullable=False, default=1)

class Deploy(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'deploy'
    # ====== Fields =============================
    # Here we define columns for the table deploy.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    title=Column(String(255))
    inventoryuuid = Column(String(11), nullable=False)
    group_uuid = Column(String(11))
    pathpackage = Column(String(100), nullable=False)
    jid_relay = Column(String(255), nullable=False)
    jidmachine = Column(String(255), nullable=False)
    state = Column(String(45), nullable=False)
    sessionid = Column(String(45), nullable=False)
    start = Column(DateTime, default=datetime.datetime.now)
    startcmd = Column(DateTime, default=None)
    endcmd = Column(DateTime, default=None)
    result = Column(Text )
    host = Column(String(255), nullable=False)
    user = Column(String(45), nullable=False, default = "")
    login = Column(String(45), nullable=False)
    command = Column(Integer)
    macadress=Column(String(255))
    syncthing = Column(Integer)

class Cluster_resources(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'cluster_resources'
    # ====== Fields =============================
    hostname = Column(String(45))
    jidmachine = Column(String(255), nullable=False)
    jidrelay = Column(String(255), nullable=False)
    startcmd = Column(DateTime, default=None)
    endcmd = Column(DateTime, default=None)
    login = Column(String(45), nullable=False)
    sessionid = Column(String(45), nullable=False)

class Command_qa(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'command_qa'
    # ====== Fields =============================
    # Here we define columns for the table Command_qa.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    command_name = Column(String(45), nullable=False, default = "")
    command_action = Column(String(500), nullable=False)
    command_login = Column(String(45), nullable=False)
    command_os = Column(String(45))
    command_start = Column(DateTime, default=datetime.datetime.now)
    command_grp = Column(String(11), default=None)
    command_machine = Column(String(11), default=None)

class Command_action(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'command_action'
    # ====== Fields =============================
    # Here we define columns for the table Command_qa.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    date = Column(DateTime, default=datetime.datetime.now)
    command_id = Column(Integer, nullable=False)
    session_id = Column(String(45), nullable=False)
    typemessage = Column(String(20), default = "log")
    command_result = Column(Text )
    target = Column(String(45), nullable=False)

class ParametersDeploy(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'parameters_deploy'
    # ====== Fields =============================
    command = Column(Integer)
    dictionary_data = Column(Text)
    data1 = Column(String(45))
    data2 = Column(String(45))
    data3 = Column(String(45))
    id_machine = Column(Integer)

class Has_login_command(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'has_login_command'
    # ====== Fields =============================
    # Here we define columns for the table deploy.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    login = Column(String(45), nullable = False)
    command = Column(Integer, nullable=False)
    start_exec_on_time = Column(DateTime, default=None)
    grpid = Column(Integer, default = None)
    nb_machine_for_deploy = Column(Integer, default = None)
    start_exec_on_nb_deploy = Column(Integer, default = None)
    count_deploy_progress= Column(Integer, default = 0)
    parameters_deploy = Column(Text, default=None)
    rebootrequired = Column(Boolean, default=False)
    shutdownrequired = Column(Boolean, default=False)
    bandwidth = Column(Integer, default = 0)
    syncthing = Column(Integer, default = 0)
    params_json = Column(Text, default=None)

class Organization(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'organization'
    # ====== Fields =============================
    # Here we define columns for the table organization.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)

class Packages_list(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'packageslist'
    # ====== Fields =============================
    # Here we define columns for the table packageslist.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    organization_id= Column(Integer, nullable=False)
    packageuuid = Column(String(45), nullable=False)

class Organization_ad(Base):
    # ====== Table name =========================
    __tablename__ = 'organization_ad'
    # ====== Fields =============================
    # Here we define columns for the table organization_AD.
    # Notice that each column is also a normal Python instance attribute.
    id_inventory = Column(Integer, primary_key=True, autoincrement=False)
    jiduser = Column(String(80), nullable=False)
    ouuser = Column(String(120), nullable=False)
    oumachine = Column(String(120), nullable=False)
    hostname = Column(String(100), nullable=False)
    username = Column(String(60), nullable=False)

class Substituteconf(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'substituteconf'
    # ====== Fields =============================
    # Here we define columns for the table substituteconf.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    type = Column(String(45), nullable=False)
    jidsubtitute = Column(String(255), nullable=False)
    countsub =  Column(Integer, nullable=False, default = 0)
    relayserver_id   = Column(Integer, ForeignKey('relayserver.id'), nullable=False)
    relayserver = relationship(RelayServer)
################################
class Agentsubcription(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'agent_subcription'
    # ====== Fields =============================
    # Here we define columns for the table agent_subcription.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

class Subcription(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'subcription'
    # ====== Fields =============================
    # Here we define columns for the table subcription.
    # Notice that each column is also a normal Python instance attribute.
    #id = Column(Integer, primary_key=True)
    macadress = Column(String(15), nullable=False)
    # ====== ForeignKey =============================
    idagentsubcription   = Column(Integer, ForeignKey('agent_subcription.id'), nullable=False)
    agent_subcription = relationship(Agentsubcription)
################################
