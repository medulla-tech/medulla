# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
    Enum,
)  # LargeBinary
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()


class XmppMasterDBObj(DBObj):
    # All XmppMaster tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Qa_custom_command(Base):
    # # ====== Table name =========================
    __tablename__ = "qa_custom_command"
    # # ====== Fields =============================
    namecmd = Column(String(45), primary_key=True)
    user = Column(String(45), primary_key=True)
    os = Column(String(45), primary_key=True)
    customcmd = Column(Text, nullable=False)
    description = Column(String(45), nullable=False, default="")


class Logs(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "logs"
    # ====== Fields =============================
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    type = Column(String(6), nullable=False, default="noset")
    date = Column(DateTime, default=datetime.datetime.now)
    text = Column(Text, nullable=False)
    sessionname = Column(String(20), nullable=False, default="")
    priority = Column(Integer, default=0)
    who = Column(String(45), nullable=False, default="")
    how = Column(String(255), nullable=False, default="")
    why = Column(String(255), nullable=False, default="")
    module = Column(String(45), nullable=False, default="")
    action = Column(String(45), nullable=False, default="")
    touser = Column(String(45), nullable=False, default="")
    fromuser = Column(String(45), nullable=False, default="")


class UserLog(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "userlog"
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    msg = Column(String(255), nullable=False)
    datelog = Column(DateTime, default=datetime.datetime.now)
    type = Column(String(10), nullable=False, default="info")


################################
class Syncthingsync(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "syncthingsync"
    # ====== Fields =============================
    # Here we define columns for the table syncthingsync.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    uuidpackage = Column(String(40), nullable=False)
    typesynchro = Column(String(10), nullable=False, default="create")
    relayserver_jid = Column(String(255))
    watching = Column(String(3), nullable=False, default="yes")
    date = Column(DateTime, default=datetime.datetime.utcnow)


# #########DEPLOY PAR SYNCTHING######################
class Syncthing_deploy_group(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "syncthing_deploy_group"
    # ====== Fields =============================
    # Here we define columns for the table syncthing_deploy_group.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    namepartage = Column(String(80), nullable=False)
    directory_tmp = Column(String(80), nullable=False)
    dateend = Column(DateTime, default=datetime.datetime.now)
    package = Column(String(90), nullable=False)
    status = Column(String(6), nullable=False)
    grp_parent = Column(Integer, nullable=False)
    cmd = Column(Integer, nullable=False)
    nbtransfert = Column(Integer, nullable=False, default=0)


class Syncthing_ars_cluster(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "syncthing_ars_cluster"
    # ====== Fields =============================
    # Here we define columns for the table syncthing_ars_cluster.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    numcluster = Column(Integer, nullable=False)
    namecluster = Column(String(45))
    liststrcluster = Column(Text, nullable=False)
    arsmastercluster = Column(String(255), nullable=False)
    devivesyncthing = Column(String(512), nullable=False)
    keypartage = Column(String(255))
    type_partage = Column(String(45))
    # ====== ForeignKey =============================
    # machines_id = Column(Integer, nullable=False)
    fk_deploy = Column(Integer, ForeignKey("syncthing_deploy_group.id"), nullable=False)
    syncthing_deploy_group = relationship(Syncthing_deploy_group)


class Syncthing_machine(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "syncthing_machine"
    # ====== Fields =============================
    # Here we define columns for the table syncthing_machine.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    jidmachine = Column(String(255), nullable=False)
    inventoryuuid = Column(String(45), nullable=False)
    title = Column(String(255))
    jid_relay = Column(String(255), nullable=False)
    cluster = Column(String(1024), nullable=False)
    pathpackage = Column(String(100), nullable=False)
    state = Column(String(45), nullable=False)
    sessionid = Column(String(45), nullable=False)
    start = Column(DateTime, nullable=False)
    startcmd = Column(DateTime, nullable=False)
    endcmd = Column(DateTime, nullable=False)
    user = Column(String(45), nullable=False)
    command = Column(Integer, nullable=False)
    group_uuid = Column(Integer, nullable=False)
    login = Column(String(45))
    macadress = Column(String(255))
    syncthing = Column(Integer, nullable=False)
    result = Column(Text, nullable=False)
    comment = Column(String(255))
    progress = Column(Integer, nullable=False, default=0)
    fk_arscluster = Column(
        Integer, ForeignKey("syncthing_ars_cluster.id"), nullable=False
    )
    syncthing_ars_cluster = relationship(Syncthing_ars_cluster)


class Glpi_entity(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "glpi_entity"
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    complete_name = Column(String(512), nullable=False)
    name = Column(String(45), nullable=False)
    glpi_id = Column(Integer, nullable=False)

    def __repr__(self):
        return "<entity('%s','%s', '%s')>" % (
            self.name,
            self.complete_name,
            self.glpi_id,
        )

    def get_data(self):
        return {
            "id": self.id,
            "complete_name": self.complete_name,
            "name": self.name,
            "glpi_id": self.glpi_id,
        }


class Glpi_location(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "glpi_location"
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    complete_name = Column(String(512), nullable=False)
    name = Column(String(45), nullable=False)
    glpi_id = Column(Integer, nullable=False)

    def __repr__(self):
        return "<location('%s','%s', '%s')>" % (
            self.name,
            self.complete_name,
            self.glpi_id,
        )

    def get_data(self):
        return {
            "id": self.id,
            "complete_name": self.complete_name,
            "name": self.name,
            "glpi_id": self.glpi_id,
        }


class Machines(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "machines"
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    jid = Column(String(255), nullable=False)
    uuid_serial_machine = Column(String(45))
    need_reconf = Column(Boolean, nullable=False, default=0)
    enabled = Column(Boolean, unique=False)
    platform = Column(String(60))
    hostname = Column(String(45), nullable=False)
    archi = Column(String(45), nullable=False)
    uuid_inventorymachine = Column(String(45), nullable=False)
    ippublic = Column(String(20))
    ip_xmpp = Column(String(45))
    subnetxmpp = Column(String(45))
    macaddress = Column(String(45))
    agenttype = Column(String(20))
    classutil = Column(String(20))
    urlguacamole = Column(String(255))
    groupdeploy = Column(String(80))
    picklekeypublic = Column(String(550))
    ad_ou_machine = Column(Text)
    ad_ou_user = Column(Text)
    kiosk_presence = Column(Enum("False", "True"))
    lastuser = Column(String(45))
    keysyncthing = Column(String(70), default="")
    glpi_description = Column(String(90), default="")
    glpi_owner_firstname = Column(String(45), default="")
    glpi_owner_realname = Column(String(45), default="")
    glpi_owner = Column(String(45), default="")
    model = Column(String(45), default="")
    manufacturer = Column(String(45), default="")
    # ====== ForeignKey =============================
    # machines_id = Column(Integer, nullable=False)
    glpi_entity_id = Column(Integer, ForeignKey("glpi_entity.id"))
    glpi_entity = relationship(Glpi_entity)
    glpi_location_id = Column(Integer, ForeignKey("glpi_location.id"))
    glpi_location = relationship(Glpi_location)


class Glpi_Register_Keys(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "glpi_register_keys"
    # ====== Fields =============================
    # Here we define columns for the table machines.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    name = Column(String(90), nullable=False)
    value = Column(String(90), nullable=False)
    comment = Column(String(90))
    # ====== ForeignKey =============================
    machines_id = Column(Integer, ForeignKey("machines.id"))
    machines = relationship(Machines)

    def __repr__(self):
        return "<register_keys('%s','%s', '%s', '%s')>" % (
            self.name,
            self.value,
            self.comment,
            self.machines_id,
        )

    def get_data(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "comment": self.comment,
            "machines_id": self.machines_id,
        }


class Network(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "network"
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
    # machines_id = Column(Integer, nullable=False)
    machines_id = Column(Integer, ForeignKey("machines.id"))
    machines = relationship(Machines)


class RelayServer(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "relayserver"
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    urlguacamole = Column(String(255))
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
    enabled = Column(Boolean, unique=False)
    mandatory = Column(Boolean, nullable=False, default=1)
    switchonoff = Column(Boolean, nullable=False, default=1)
    classutil = Column(String(10))
    moderelayserver = Column(String(7))
    keysyncthing = Column(String(70), default="")
    syncthing_port = Column(Integer, default=23000)


class Regles(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "rules"
    # ====== Fields =============================
    # Here we define columns for the table network.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(45))
    description = Column(String(45))
    level = Column(Integer)


class Users(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "users"
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
    creation_user = Column(DateTime, nullable=True)
    last_modif = Column(DateTime, nullable=True)


class Has_machinesusers(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "has_machinesusers"
    # ====== ForeignKey =============================
    machines_id = Column(Integer, ForeignKey("machines.id"))
    users_id = Column(Integer, ForeignKey("users.id"))
    machines = relationship(Machines)
    users = relationship(Users)


class Has_relayserverrules(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "has_relayserverrules"
    # ====== ForeignKey =============================
    rules_id = Column(Integer, ForeignKey("rules.id"))
    relayserver_id = Column(Integer)
    subject = Column(String(45))
    order = Column(Integer)
    rules = relationship(Regles)


class Has_guacamole(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "has_guacamole"
    # ====== Fields =============================
    # Here we define columns for the table has_guacamole.
    # Notice that each column is also a normal Python instance attribute.
    idguacamole = Column(Integer)
    protocol = Column(String(10))
    # ====== ForeignKey =============================
    machine_id = Column(Integer, ForeignKey("machines.id"))
    machines = relationship(Machines)


class Has_cluster_ars(Base, XmppMasterDBObj):
    # # ====== Table name =========================
    __tablename__ = "has_cluster_ars"
    # # ====== ForeignKey =============================
    id_ars = Column(Integer)
    id_cluster = Column(Integer)


class Cluster_ars(Base, XmppMasterDBObj):
    # # ====== Table name =========================
    __tablename__ = "cluster_ars"
    # # ====== ForeignKey =============================
    name = Column(String(40))
    description = Column(String(255))


class Version(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "version"
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    active = Column(TINYINT(1), nullable=False, default=1)


class Deploy(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "deploy"
    # ====== Fields =============================
    # Here we define columns for the table deploy.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    title = Column(String(255))
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
    result = Column(Text)
    host = Column(String(255), nullable=False)
    user = Column(String(45), nullable=False, default="")
    login = Column(String(45), nullable=False)
    command = Column(Integer)
    macadress = Column(String(255))
    syncthing = Column(Integer)


class Cluster_resources(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "cluster_resources"
    # ====== Fields =============================
    hostname = Column(String(255))
    jidmachine = Column(String(255), nullable=False)
    jidrelay = Column(String(255), nullable=False)
    startcmd = Column(DateTime, default=None)
    endcmd = Column(DateTime, default=None)
    login = Column(String(45), nullable=False)
    sessionid = Column(String(45), nullable=False)


class Command_qa(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "command_qa"
    # ====== Fields =============================
    # Here we define columns for the table Command_qa.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    command_name = Column(String(45), nullable=False, default="")
    command_action = Column(String(500), nullable=False)
    command_login = Column(String(45), nullable=False)
    command_os = Column(String(45))
    command_start = Column(DateTime, default=datetime.datetime.now)
    command_grp = Column(String(11), default=None)
    command_machine = Column(String(11), default=None)
    jid_machine = Column(String(255), nullable=False)


class Command_action(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "command_action"
    # ====== Fields =============================
    # Here we define columns for the table Command_qa.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    # Warning, if you modify the wrapper, you also have to change it in log.py
    date = Column(DateTime, default=datetime.datetime.now)
    command_id = Column(Integer, nullable=False)
    session_id = Column(String(45), nullable=False)
    typemessage = Column(String(20), default="log")
    command_result = Column(Text)
    target = Column(String(45), nullable=False)
    jid_target = Column(String(255), nullable=False)


class ParametersDeploy(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "parameters_deploy"
    # ====== Fields =============================
    command = Column(Integer)
    dictionary_data = Column(Text)
    data1 = Column(String(45))
    data2 = Column(String(45))
    data3 = Column(String(45))
    id_machine = Column(Integer)


class Has_login_command(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "has_login_command"
    # ====== Fields =============================
    # Here we define columns for the table deploy.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    login = Column(String(45), nullable=False)
    command = Column(Integer, nullable=False)
    start_exec_on_time = Column(DateTime, default=None)
    grpid = Column(Integer, default=None)
    nb_machine_for_deploy = Column(Integer, default=None)
    start_exec_on_nb_deploy = Column(Integer, default=None)
    count_deploy_progress = Column(Integer, default=0)
    parameters_deploy = Column(Text, default=None)
    rebootrequired = Column(Boolean, default=False)
    shutdownrequired = Column(Boolean, default=False)
    bandwidth = Column(Integer, default=0)
    syncthing = Column(Integer, default=0)
    params_json = Column(Text, default=None)


class Organization(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "organization"
    # ====== Fields =============================
    # Here we define columns for the table organization.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)


class Packages_list(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "packageslist"
    # ====== Fields =============================
    # Here we define columns for the table packageslist.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, nullable=False)
    packageuuid = Column(String(45), nullable=False)


class Organization_ad(Base):
    # ====== Table name =========================
    __tablename__ = "organization_ad"
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
    __tablename__ = "substituteconf"
    # ====== Fields =============================
    # Here we define columns for the table substituteconf.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    type = Column(String(45), nullable=False)
    jidsubtitute = Column(String(255), nullable=False)
    countsub = Column(Integer, nullable=False, default=0)
    relayserver_id = Column(Integer, ForeignKey("relayserver.id"), nullable=False)
    relayserver = relationship(RelayServer)


################################


class Agentsubscription(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "agent_subscription"
    # ====== Fields =============================
    # Here we define columns for the table agent_subscription.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class Subscription(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "subscription"
    # ====== Fields =============================
    # Here we define columns for the table subscription.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    macadress = Column(String(15), nullable=False)
    # ====== ForeignKey =============================
    idagentsubscription = Column(
        Integer, ForeignKey("agent_subscription.id"), nullable=False
    )
    agent_subscription = relationship(Agentsubscription)


# ###############################


class Def_remote_deploy_status(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "def_remote_deploy_status"
    # ====== Fields =============================
    # Here we define columns for the table def_remote_deploy_status.
    # Notice that each column is also a normal Python instance attribute.

    # id = Column(Integer, primary_key=True)
    regex_logmessage = Column(String(80), nullable=False)
    status = Column(String(80), nullable=False)
    label = Column(String(255), nullable=False)


# ###### QA For Relays #######
# Qa_relay_command describe a qa for relayserver


class Qa_relay_command(Base, XmppMasterDBObj):
    __tablename__ = "qa_relay_command"
    user = Column(String(45), nullable=False)  # Relay Qa Owner
    name = Column(String(45), nullable=False)  # Relay Qa Name
    script = Column(Text, nullable=False)  # Relay Qa Script
    description = Column(String(45))  # Relay Qa Description


class Qa_relay_launched(Base, XmppMasterDBObj):
    __tablename__ = "qa_relay_launched"
    id_command = Column(Integer, nullable=False)  # Qa Reference
    user_command = Column(String(45), nullable=False)  # Relay Qa Owner
    command_start = Column(
        DateTime, default=datetime.datetime.now  # Relay Qa launched date
    )
    command_cluster = Column(String(45))  # Relay Qa target if the target is a cluster
    command_relay = Column(String(45))  # Relay Qa target if the target is a uniq relay


class Qa_relay_result(Base, XmppMasterDBObj):
    __tablename__ = "qa_relay_result"
    id_command = Column(
        Integer, nullable=False  # Quick get a ref to the initial command
    )
    # Reference to the specialized command (launched command)
    launched_id = Column(Integer, nullable=False)
    session_id = Column(String(45), nullable=False)  # xmpp session id
    typemessage = Column(String(20), nullable=False, default="log")
    command_result = Column(Text)
    # If uniq command : relay, if cluster command : jid of the cluster member
    relay = Column(String(45), nullable=False)


class Uptime_machine(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "uptime_machine"
    # ====== Fields =============================
    # Here we define columns for the table uptime_machine.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    hostname = Column(String(100), nullable=False)
    jid = Column(String(255), nullable=False)
    status = Column(Boolean, unique=False)
    updowntime = Column(Integer, nullable=False, default=0)
    date = Column(DateTime, default=datetime.datetime.now)
    timetempunix = Column(Integer, default=None)
    md5agentversion = Column(String(32), default=None)
    version = Column(String(10), default=None)


class MyTypeenum(enum.Enum):
    """
    This class defines the device type domain
    """

    thermalprinter = "thermalprinter"
    nfcReader = "nfcReader"
    opticalReader = "opticalReader"
    cpu = "cpu"
    memory = "memory"
    storage = "storage"
    network = "network"


class Mystatusenum(enum.Enum):
    """
    This class defines the status domain
    """

    ready = "ready"
    busy = "busy"
    warning = "warning"
    error = "error"
    disable = "disable"


class Mon_machine(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_machine"
    # ====== Fields =============================
    # Here we define columns for the table mon_machine.
    # Notice that each column is also a normal Python instance attribute.
    #  id = Column(Integer, primary_key=True)
    machines_id = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now)
    hostname = Column(String(100), nullable=False)
    statusmsg = Column(Text)


class Mon_devices(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_devices"
    # ====== Fields =============================
    # Here we define columns for the table mon_devices.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    mon_machine_id = Column(Integer, nullable=False)
    device_type = Column(String(45), nullable=False, default="opticalReader")
    serial = Column(String(45), default=None)
    firmware = Column(String(10), default=None)
    status = Column(String(45), nullable=False, default="ready")
    alarm_msg = Column(String(45), default=None)
    doc = Column(Text, default=None)


class Mon_device_service(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_device_service"
    # ====== Fields =============================
    # Here we define columns for the table mon_device_service.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    device_type = Column(String(45), nullable=False, default="opticalReader")
    enable = Column(Boolean, default=True)
    structure_json_controle = Column(Text, nullable=False)
    html_form = Column(Text)
    mon_machine_id = Column(Integer, nullable=False)


class Mon_rules(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_rules"
    # ====== Fields =============================
    # Here we define columns for the table mon_device_service.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    enable = Column(Integer, nullable=False, default=1)
    hostname = Column(String(255), default=None)
    device_type = Column(String(255), nullable=False, default="opticalReader")
    binding = Column(Text)
    succes_binding_cmd = Column(Text, default=None)
    no_success_binding_cmd = Column(Text, default=None)
    error_on_binding = Column(Text, default=None)
    type_event = Column(String(255), default=None)
    user = Column(String(255), default=None)
    comment = Column(String(1024))
    os = Column(String(45), default=None)
    type_machine = Column(String(45), default=None)


class Mon_event(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_event"
    # ====== Fields =============================
    # Here we define columns for the table mon_device_service.
    # Notice that each column is also a normal Python instance attribute.
    # id = Column(Integer, primary_key=True)
    status_event = Column(Integer, default=1)
    type_event = Column(String(255), default=None)
    cmd = Column(Text)
    machines_id = Column(Integer, nullable=False)
    id_rule = Column(Integer, nullable=False)
    id_device = Column(Integer, nullable=False)
    parameter_other = Column(String(1024), nullable=True)
    ack_user = Column(String(90), nullable=True)
    ack_date = Column(DateTime, default=datetime.datetime.now)


class Mon_panels_template(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "mon_panels_template"
    # ====== Fields =============================
    # Here we define columns for the table mon_panels_template.
    # Notice that each column is also a normal Python instance attribute.
    name_graphe = Column(String(255), nullable=False)
    template_json = Column(Text, nullable=False)
    type_graphe = Column(String(255), nullable=False)
    parameters = Column(String(1024), default="{}")
    status = Column(Boolean, default=True)
    comment = Column(String(1024), default="")


class Update_data(Base):
    # ====== Table name =========================
    __tablename__ = "update_data"
    # ====== Fields =============================
    updateid = Column(String(38), primary_key=True)
    revisionid = Column(String(16), nullable=False, default="")
    creationdate = Column(DateTime, default=datetime.datetime.now)
    compagny = Column(String(36), default="")
    product = Column(String(512), default="")
    productfamily = Column(String(100), default="")
    updateclassification = Column(String(36), default="")
    prerequisite = Column(String(2048), default="")
    title = Column(String(500), default="")
    description = Column(String(2048), default="")
    msrcseverity = Column(String(16), default="")
    msrcnumber = Column(String(16), default="")
    kb = Column(String(16), default="")
    languages = Column(String(16), default="")
    category = Column(String(80), default="")
    supersededby = Column(String(2048), default="")
    supersedes = Column(Text, default=None)
    payloadfiles = Column(String(1024), default="")
    revisionnumber = Column(String(30), default="")
    bundledby_revision = Column(String(30), default="")
    isleaf = Column(String(6), default="")
    issoftware = Column(String(30), default="")
    deploymentaction = Column(String(30), default="")
    title_short = Column(String(500), default="")


class Up_black_list(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "up_black_list"
    # ====== Fields =============================
    updateid = Column(String(38), nullable=False)
    userjid_regexp = Column(String(180), nullable=False)
    enable_rule = Column(Boolean, unique=True)
    type_rule = Column(String(2), nullable=False, default="id")


class Up_machine_windows(Base):
    # ====== Table name =========================
    __tablename__ = "up_machine_windows"
    # ====== Fields =============================
    id_machine = Column(Integer, primary_key=True)
    update_id = Column(String(38), primary_key=True)
    kb = Column(String(45), default="")
    curent_deploy = Column(Boolean, unique=False)
    required_deploy = Column(Boolean, unique=False)
    start_date = Column(DateTime, default=None)
    end_date = Column(DateTime, default=None)
    intervals = Column(String(256), nullable=True, default=None)
    msrcseverity = Column(String(16), nullable=True)


class Up_white_list(Base):
    # ====== Table name =========================
    __tablename__ = "up_white_list"
    # ====== Fields =============================
    updateid = Column(String(38), primary_key=True)
    creationdate = Column(DateTime, default=datetime.datetime.now)
    title = Column(String(1024), default="")
    description = Column(String(3096), default="")
    kb = Column(String(16), default="")
    title_short = Column(String(1024), default="")
    valided = Column(Boolean, unique=False)


class Up_gray_list(Base):
    # ====== Table name =========================
    __tablename__ = "up_gray_list"
    # ====== Fields =============================
    updateid = Column(String(38), primary_key=True)
    revisionid = Column(String(16), nullable=False, default="")
    creationdate = Column(DateTime, default=datetime.datetime.now)
    title = Column(String(1024), default="")
    description = Column(String(3096), default="")
    updateid_package = Column(String(38))
    kb = Column(String(16), default="")
    supersededby = Column(String(3072), default="")
    payloadfiles = Column(String(2048), default="")
    title_short = Column(String(1024), default="")
    valided = Column(Boolean, unique=False)
    validity_date = Column(DateTime, default=datetime.datetime.now)


class Mmc_module_actif(Base):
    # ====== Table name =========================
    __tablename__ = "mmc_module_actif"
    # ====== Fields =============================
    # Here we define columns for the table update_machine.
    # Notice that each column is also a normal Python instance attribute.
    name_module = Column(String(38), primary_key=True)
    enable = Column(Boolean, nullable=False, default=False)
    informations = Column(String(1024), default="")


class Up_history(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = "up_history"
    # ====== Fields =============================
    update_id = Column(String(38))
    id_machine = Column(Integer)
    jid = Column(String(255), nullable=False)
    update_list = Column(Enum("white", "gray"))
    required_date = Column(DateTime, default=None)
    curent_date = Column(DateTime, default=None)
    deploy_date = Column(DateTime, default=None)
    delete_date = Column(DateTime, default=None)
    command = Column(Integer)
    id_deploy = Column(Integer)
    deploy_title = Column(String(255))


class Users_adgroups(Base):
    # ====== Table name =========================
    __tablename__ = "users_adgroups"
    # ====== Fields =============================
    lastuser = Column(String(255), nullable=False, primary_key=True)
    adname = Column(String(255), nullable=False, primary_key=True)

class Up_machine_activated(Base):
    # ====== Table name =========================
    __tablename__ = "up_machine_activated"
    # ====== Fields =============================
    kb = Column(String(45), default="")
    id_machine = Column(Integer, primary_key=True)
    glpi_id = Column(Integer, nullable=False)
    hostname = Column(String(45))
    jid = Column(String(255))
    entities_id = Column(Integer, default=0)
    update_id = Column(String(45), nullable=False, primary_key=True)
    curent_deploy = Column(Boolean, nullable=True, default=0)
    required_deploy =Column(Boolean, nullable=True, default=0)
    start_date =Column(DateTime, default=None)
    end_date =Column(DateTime, default=None)
    intervals =Column(String(255), nullable=True)
    msrcseverity =Column(String(16))
    list = Column(String(5), nullable=False)


"""
This code is kept here as a comment, "if" we need to use it
and not use the automatic table anymore.
DO NOT REMOVE.
class Update_machine(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'update_machine'
    # ====== Fields =============================
    # Here we define columns for the table update_machine.
    # Notice that each column is also a normal Python instance attribute.
    hostname = Column(String(120), nullable=False)
    jid = Column(String(255), nullable=False)
    status  = Column(String(255), nullable=False, default="ready")
    descriptor = Column(Text, nullable=False)
    md5 = Column(String(255), nullable=False)
    date_creation  =  Column(DateTime, default=datetime.datetime.now)
    ars = Column(String(255), nullable=False,default="")

class Ban_machines(Base, XmppMasterDBObj):
    # ====== Table name =========================
    __tablename__ = 'ban_machines'
    # ====== Fields =============================
    # Here we define columns for the table ban_machines.
    # Notice that each column is also a normal Python instance attribute.
    jid = Column(String(255), nullable=False)
    date  =  Column(DateTime, default=datetime.datetime.now)
    ars_server     = Column(String(255), nullable=False,default="")

class Up_packages(Base):
    # ====== Table name =========================
    __tablename__ = "up_packages"
    # ====== Fields =============================
    updateid = Column(String(38), primary_key=True)
    kb = Column(String(45),  default="")
    revisionid = Column(String(45),  default="")
    title = Column(String(1024),  default="")
    id_machine = Column(Integer)
    updateid_package = Column(String(38))
    payloadfiles = Column(String(1024),  default="")
"""
