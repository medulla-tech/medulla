#!/usr/bin/python3
import os
import sys
from configparser import ConfigParser

from datetime import datetime
from datetime import timedelta


from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from mmc.plugins.urbackup.urwrapper import UrApiWrapper
import logging


Base = declarative_base()

class Profiles(Base):
    __tablename__="profiles"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    entity_id = Column(Integer, nullable=False)
    profile_uuid = Column(String(255), nullable=False)
    profile_name = Column(String(255), nullable=False)

class ClientState(Base):
    __tablename__ = "client_state"
    client_id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    client_jid = Column(String(255), nullable=False)
    state = Column(Integer, nullable=False)
    authkey= Column(String(255), nullable=False)

class MachinesProfiles(Base):
    __tablename__ = "machines_profiles"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    machine_jid = Column(String(255), nullable=False)
    profile_id = Column(Integer, nullable=False)

class Logs(Base):
    __tablename__ = "all_logs"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    client_id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    loglevel = Column(Integer, nullable=False, default=-1)
    msg= Column(String(255), nullable=False)
    time = Column(Integer, nullable=False)



if __name__ == "__main__":
    configfile = os.path.join("/","etc", "mmc", "plugins", "urbackup.ini")
    
    # Get config
    config = ConfigParser()
    config.read(configfile)
    config.read("%s.local"%configfile)

    dbdriver = config.get("database", "dbdriver")
    dbhost = config.get("database", "dbhost")
    dbport = int(config.get("database", "dbport"))
    dbuser = config.get("database", "dbuser")
    dbpasswd = config.get("database", "dbpasswd")
    dbname = config.get("database", "dbname")

    # Create engine
    url = f"{dbdriver}://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)

    api = UrApiWrapper()

    # Delete all the logs older than 90 days
    with Session(engine) as session:
        d = datetime.now()
        r = d - timedelta(days=90)
        query = session.query(Logs).filter(Logs.time<r.timestamp()).delete()
        session.commit()
        session.flush()


    # Get profiles associated to entities
    entities = []
    with Session(engine) as session:
        query = session.query(Profiles).all()

        if query is None:
            sys.exit(0)

        for profile in query:
            entities.append({
                "id" : profile.id,
                "entity_id": profile.entity_id,
                "profile_uuid" : profile.profile_uuid,
                "profile_name": profile.profile_name,
                "client_ids" : []
            })

    # Get all clients for each entity
    for profile in entities:
        with Session(engine) as session:
            query = session.query(ClientState.client_id,ClientState.client_jid)\
                .join(MachinesProfiles, ClientState.client_jid == MachinesProfiles.machine_jid)\
                .join(Profiles, MachinesProfiles.profile_id == Profiles.id)\
                .filter(Profiles.entity_id == profile["entity_id"]).distinct().all()

            if query is None:
                continue

            # Get logs for each clients
            for element in query:
                profile["client_ids"].append(element.client_id)
                _logs = api.get_logs(element.client_id)
                logs = _logs["content"] if "content" in _logs else []
                if "logdata" in logs:
                    ids = []
                    ids_to_add = []
                    for log in logs["logdata"]:
                        ids.append(log["id"])

                    # Copy the list of ids into ids_to_add. Later we will remove the matches
                    ids_to_add = list(ids)

                    # Got the existing logs
                    query = session.query(Logs.id).filter(Logs.id.in_(ids))
                    if query is not None:
                        for row in query:
                            if row.id in ids_to_add:
                                ids_to_add.remove(row.id)

                    # Add logs only if not already present
                    for log in logs["logdata"]:
                        if log["id"] in ids_to_add:
                            tmp = Logs()
                            tmp.client_id = element.client_id
                            tmp.id = log["id"]
                            tmp.loglevel = log["loglevel"]
                            tmp.msg = log["msg"]
                            tmp.time = log["time"]

                            try:
                                session.add(tmp)
                                session.commit()
                                session.flush()
                            except Exception as e:
                                logging.getLogger().error(str(e))
                                continue
                    print(element)
                    print("Updating %s logs for entity %s client %s (%s)"%(len(ids_to_add), profile["entity_id"], element.client_id, element.client_jid))

