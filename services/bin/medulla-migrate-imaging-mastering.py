#!/usr/bin/python3 
# SPDX-License-Identifier : LGPL-V3

# File: medulla-migrate-imaging-mastering.py

import socket
from configparser import ConfigParser
import os
import sys
import subprocess
import re
import logging
import json
import base64
import zlib
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm.session import Session
from sqlalchemy import (
    text,
    and_,
    or_,
    func,
    select,
    insert,
    update,
    delete
)
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger()

"""mod is a wrapper for the config, session factory, engine and related information on each needed modules."""
mod = {}


def get_config_path(name: str) ->str:
    """Get the configuration file path for the given plugin name."""

    return os.path.join("/", "etc", "mmc", "plugins", "%s.ini"%name)

def get_config(file:str, overload:str = ".local")->ConfigParser|None:
    """Load the configuration from the given file, optionally overloading with a local file.
    
    Args:
        file (str): The path to the configuration file.
        overload (str, optional): The suffix for the local overload file. Defaults to ".local".

    Returns:
        ConfigParser|None: The loaded configuration parser object, or None if the file does not exist.
    """
    config = None

    if os.path.exists(file) is False:
        return None
    
    config = ConfigParser()
    config.read(file)

    if os.path.exists("%s%s"%(file, overload)):
        config.read("%s%s"%(file, overload))

    return config


def activate_module_mastering():
    """Activate the mastering module if it is present and not disabled.

    Returns:
        bool: True if the module was activated or already active, False otherwise.
    """

    global mod

    if "mastering" not in mod:
        return False

    _config = mod["mastering"]["config"]
    if _config.has_option("main", "disable"):
        if _config.getboolean("main", "disable") == True:
            _config["main"]["disable"] = "0"
            filename = "%s.local"%mod["mastering"]["config_file"]
            with open(filename, "w") as fb:
                _config.write(fb)
                fb.close()

    return True


def get_url(config:ConfigParser) -> str:
    """Get the database URL from the given configuration.

    Args:
        config (ConfigParser): The configuration parser object containing database settings.

    Returns:
        str: The database URL constructed from the configuration, or an empty string if the configuration is None.
    """

    if config is None:
        return ""

    url = ""
    try:
        driver = ""
        if config.has_option("database", "dbdriver"):
            driver = config.get("database", "dbdriver")

        host = ""
        if config.has_option("database", "dbhost"):
            host = config.get("database", "dbhost")

        port = 3306
        if config.has_option("database", "dbport"):
            port = config.get("database", "dbport")

        name =""
        if config.has_option("database", "dbname"):
            name = config.get("database", "dbname")

        user = ""
        if config.has_option("database", "dbuser"):
            user = config.get("database", "dbuser")
        
        passwd = ""
        if config.has_option("database", "dbpasswd"):
            passwd = config.get("database", "dbpasswd")
        
        url = f"{driver}://{user}:{passwd}@{host}:{port}/{name}"
    except Exception as e:
        logger.error(e)
        pass
    return url


def _session(name) -> None|Session:
    """Get a session for the specified module.

    Args:
        name (str): The name of the module to get the session for.

    Returns:
        Session|None: The session object for the module, or None if the module is not found.
    """

    global mod

    if name not in mod:
        return None
    session = mod[name]["session_factory"]()
    return session


def get_relays_list() -> list:
    """Get the list of relay servers from the database.
    
    Returns:
        list: A list of relay servers retrieved from the database.
    """
    relay_list = []
    with _session("xmppmaster") as session:
        query = session.query(Relayserver).all()

        if query is None:
            logger.error("No relayserver available for association")
            return relay_list

        for e in query:
            tmp = {
                "jid":e.jid,
                "nameserver" : e.nameserver,
                "package_server_ip":e.package_server_ip,
                "ipserver": e.ipserver
            }
            relay_list.append(tmp)

    return relay_list


def get_imaging_servers_list() -> list:
    """Get the list of imaging servers from the database.

    Returns:
        list: A list of imaging servers retrieved from the database.
    """
    imaging_list = []

    with _session("imaging")as session:
        stmt = (
            select(ImagingServer, Entity)\
                .join(Entity, Entity.c.id == ImagingServer.c.fk_entity)
        )
        query = session.execute(stmt)

        if query is None:
            logger.error("No ImagingServer available for association")
            return imaging_list

        for row in query:
            tmp = {
                "id":row.id,
                "eid":row.uuid.replace("UUID", ""),
                "url":row.url.split(":9990/imaging_api")[0].replace("http://", "").replace("https://", "")
            }
            imaging_list.append(tmp)

    return imaging_list



def get_matching_servers(relays, imaging_servers) -> list:
    """Get the list of matching servers based on relay and imaging server information.

    Args:
        relays (list): A list of relay servers.
        imaging_servers (list): A list of imaging servers.

    Returns:
        list: A list of matching servers with their associated rules.
    """

    # #####
    # Associate relay to imagingserver
    # #####
    matches = []
    for ims in imaging_servers:
        ip = ""
        try:
            ip = socket.gethostbyname(ims["url"])
        except:
            continue

        for relay in relays:
            if ims["url"] == relay["nameserver"]:
                logger.info("Matching rule nameserver for ImagingServer %s and %s"%(ims["url"], relay["jid"]))
                _match = {
                    "id": ims["id"],
                    "eid": ims["eid"],
                    "url": ims["url"],
                    "jid": relay["jid"],
                    "nameserver": relay["nameserver"],
                    "package_server_ip": relay["package_server_ip"],
                    "ipserver": relay["ipserver"],
                    "rule": "nameserver"
                }
                matches.append(_match)
                break

            elif ip == relay["package_server_ip"]:
                logger.info("Matching rule package_server_ip for ImagingServer %s and %s"%(ims["url"], relay["jid"]))
                _match = {
                    "id": ims["id"],
                    "eid": ims["eid"],
                    "url": ims["url"],
                    "jid": relay["jid"],
                    "nameserver": relay["nameserver"],
                    "package_server_ip": relay["package_server_ip"],
                    "ipserver": relay["ipserver"],
                    "rule": "package_server_ip"
                }
                matches.append(_match)
                break

            elif ip == relay["ipserver"]:
                logger.info("Matching rule ipserver for ImagingServer %s and %s"%(ims["url"], relay["jid"]))
                _match = {
                    "id": ims["id"],
                    "eid": ims["eid"],
                    "url": ims["url"],
                    "jid": relay["jid"],
                    "nameserver": relay["nameserver"],
                    "package_server_ip": relay["package_server_ip"],
                    "ipserver": relay["ipserver"],
                    "rule": "ipserver"
                }
                matches.append(_match)
                break
    return matches


def get_masters_from_imaging(matches:list) -> dict:
    """Get the masters associated with imaging servers based on the matching rules.

    Args:
        matches (list): A list of mat200ching servers with their associated rules.

    Returns:
        dict: A dictionary of images with their associated servers and entities.
    """
    images = {}
    with _session("imaging") as session:
        stmt = (
            select(Image, ImageOnImagingServer)
                .join(ImageOnImagingServer)
        )
        query = session.execute(stmt).all()

        # Get the images associated to the servers (= old masters )
        for e in query:
            srv = ""
            for _match in matches:
                if _match["id"] == e.fk_imaging_server:
                    srv = _match["jid"]
            if e.uuid not in images:
                images[e.uuid] = {
                    "id":e.id,
                    "name":e.name,
                    "description":e.desc,
                    "uuid":e.uuid,
                    "path":e.path,
                    "size": e.size,
                    "creation_date": e.creation_date,
                    "servers" : [],
                    "entities": []
                }
                if srv != "":
                    images[e.uuid]["servers"] = [srv]

            else:
                if e.fk_imaging_server not in images[e.uuid]["servers"] and srv != "":
                    images[e.uuid]["servers"].append(srv)
    return images



def insert_or_update_servers(matches:list) -> None:
    """Insert or update servers in the mastering database.

    Args:
        matches (list): A list of matching servers with their associated rules.

    Returns:
        None
    """

    # #####
    # Insert or update relayserver into mastering.servers
    # #####
    with _session("mastering") as session:
        for m in matches:
            query = session.query(Servers).filter(Servers.c.jid == m["jid"]).first()
            if query is None:
                logging.info("Associate server %s with entity %s"%(m["jid"], m["eid"]))
                stmt = (
                    insert(Servers)
                    .values(
                        jid=m["jid"],
                        entity_id = m["eid"]
                    )
                )
                session.execute(stmt)
                session.commit()
                session.flush()
            else:
                if query.entity_id != m["eid"]:
                    stmt = (update(Servers)
                        .where(Servers.c.jid == m["jid"])
                        .values(entity_id = m["eid"])
                    )
                    session.execute(stmt)
                    session.commit()
                    session.flush()


def associate_masters_to_servers(images:dict) -> None:
    """Associate masters to their respective servers in the mastering database.

    Args:
        images (dict): A dictionary containing image information and associated servers.

    Returns:
        None
    """
    with _session("mastering") as session:
        for uuid in images:
            stmt = select(Masters).where(Masters.c.uuid == uuid)
            query = session.execute(stmt).first()

            # We need to add the image
            if query is None:
                logger.info("Importing master %s (%s)"%(images[uuid]["name"], uuid))
                stmt = insert(Masters).values(
                    name=images[uuid]["name"],
                    description=images[uuid]["description"],
                    uuid=uuid,
                    path=images[uuid]["path"],
                    size=images[uuid]["size"],
                    creation_date=images[uuid]["creation_date"]
                )

                session.execute(stmt)
                session.commit()
                session.flush()

            # We need to associate this image to the right servers
            stmt = (
                select(MastersEntities, Servers)
                .join(Masters, Masters.c.id == MastersEntities.c.master_id)
                .join(Servers, MastersEntities.c.entity_id == Servers.c.entity_id).where(Masters.c.uuid == uuid)
            )
            query = session.execute(stmt).all()
            for row in query:
                # Remove present jids from the list
                if row.jid in images[uuid]["servers"]:
                    logger.info("master %s already associated with %s"%(uuid, row.jid))
                    images[uuid]["servers"].remove(row.jid)

            # Remaining images to associate with the server
            for jid in images[uuid]["servers"]:
                logger.info("Master %s associated to server %s"%(images[uuid]["name"], jid))
                sql = """Insert into mastersEntities(entity_id, master_id) values((select entity_id from servers where jid=:jid), (select id from masters where uuid=:uuid))"""
                binds = {
                    "jid":jid,
                    "uuid":uuid
                }
                session.execute(text(sql), binds)
                session.commit()
                session.flush()

def get_scripts_from_imaging(matches:list) -> list:
    scripts = []

    with _session("imaging") as session:
        sql = """
select 
    pis.id, 
    pis.default_name,
    pis.default_desc,
    pis.value,
    pisois.fk_imaging_server,
    e.uuid
from PostInstallScriptOnImagingServer pisois 
join PostInstallScript pis on pis.id = pisois.fk_post_install_script 
join ImagingServer ims on ims.id = pisois.fk_imaging_server 
join Entity e on e.id = ims.fk_entity
"""
        query = session.execute(text(sql)).all()
        for e in query:
            scripts.append({
                "id": e[0],
                "name": e[1],
                "description": e[2],
                "value": e[3],
                "ims": e[4],
                "entity": int(e[5].replace("UUID", "")),
            })

    return scripts


def get_meta_from_sysprep(filename:str) -> dict|None:
    """Extract metadata from a sysprep file.

    Args:
        filename (str): The name of the sysprep file.

    Returns:
        dict|None: A dictionary containing the extracted metadata, or None if the file does not exist or parsing fails.
    """
    master_path = mod["mastering"]["config"].get("master", "path")
    sysprep_path = os.path.join(os.path.dirname(master_path), "postinst", "sysprep", filename)

    if os.path.exists(sysprep_path):
        with open(sysprep_path, "r") as fb:
            line = ""
            parameters = {}
            while line := fb.readline():
                line = line.strip()
                if line.startswith("OS"):
                    line = line.replace("OS ", "")
                    parameters["os"] = line
                if line.startswith("Notes: "):
                    line = line.replace("Notes: ", "")
                    parameters["notes"] = line
                if line.startswith("date : "):
                    line = line.replace("date : ", "")
                    parameters["date"] = line
                if line.startswith("list parameters"):
                    line = line.replace("list parameters : ", "")

                    try:
                        meta = json.loads(line)
                        parameters["meta"] = meta
                        return parameters
                    except:
                        return None
                    break

    else:
        logger.error("Sysprep file not found: %s"%sysprep_path)
        return None

def insert_script(script, parameters):
    """Insert a script into the database.

    Args:
        script (dict): A dictionary containing script information.
        parameters (dict): A dictionary containing additional parameters for the script. 
            Parameters can be None, in that case, type will be bash and "payload" will be empty.

    Returns:
        None
    """
    
    # script["entity"] => entity_id
    # parameters["meta"]["type"] => type
    # script["name"] => name
    # script["description"] => description
    # script["value"] => content
    # parameters["meta"] => payload


    entity_id = script["entity"]
    # 
    _type = parameters["meta"]["type"] if parameters is not None else "bash"
    name = script["name"]
    description = script["description"]
    content = base64.b64encode(zlib.compress(script["value"].encode("utf-8")))
    payload = base64.b64encode(zlib.compress(json.dumps(parameters["meta"]).encode("utf-8"))) if parameters is not None else ""

    with _session("mastering") as session:
        query = session.query(Scripts).filter(Scripts.c.name == script["name"], Scripts.c.entity_id == script["entity"]).first()

        if query is None:
            # Insert the new script
            new_script = Scripts.insert().values(
                entity_id=entity_id,
                type=_type,
                name=name,
                description=description,
                content=content,
                payload=payload
            )
            session.execute(new_script)
            session.commit()
        else:
            logger.info("Script already exists: %s"%script["name"])


# #####
# GLOBAL SETUP
# #####

for e in ["mastering", "xmppmaster", "imaging"]:
    config_file = get_config_path(e)
    config = get_config(config_file)
    if(config == None):
        logger.error("Impossible to load configuration for %s module"%e)
        sys.exit(1)
    
    url = get_url(config)
    if url == "":
        logger.error("Impossible to generate url to connect to database %s"%e)
        sys.exit(1)

    engine = create_engine(url)
    if engine == None:
        logger.error("Impossible to create engine for module %s"%e)
        sys.exit(1)

    meta = MetaData()
    if meta == None:
        logger.error("Impossible to create meta for %s database connection"%e)
        sys.exit(1)

    meta.reflect(bind=engine)
    session_factory = sessionmaker(bind=engine)
    
    mod[e] = {
        "config_file":config_file,
        "url":url,
        "config":config,
        "engine" : engine,
        "meta": meta,
        "session_factory":session_factory
    }

# #####
# sqlalchemy binds
# #####

# Create some alias for xmppmaster tables
Relayserver = mod["xmppmaster"]["meta"].tables["relayserver"]

# Create some alias for imaging tables
ImagingServer = mod["imaging"]["meta"].tables["ImagingServer"]
Entity = mod["imaging"]["meta"].tables["Entity"]
Image = mod["imaging"]["meta"].tables["Image"]
ImageOnImagingServer = mod["imaging"]["meta"].tables["ImageOnImagingServer"]
PostInstallScript = mod["imaging"]["meta"].tables["PostInstallScript"]
PostInstallScriptOnImagingServer = mod["imaging"]["meta"].tables["PostInstallScriptOnImagingServer"]

# Create some alias for mastering tables
Servers = mod["mastering"]["meta"].tables["servers"]
Masters = mod["mastering"]["meta"].tables["masters"]
MastersEntities = mod["mastering"]["meta"].tables["mastersEntities"]
Scripts = mod["mastering"]["meta"].tables["scripts"]

if __name__ == "__main__":
    # Activate the module if not already
    activate_module_mastering()

    # Get the relays list
    relays = get_relays_list()

    # Get the imagingservers list
    imaging_servers = get_imaging_servers_list()

    # Find out which imaging server has to be associated to which relayserver
    matches = get_matching_servers(relays, imaging_servers)

    # Insert or update servers on mastering
    # It associates the jid to the  entity
    insert_or_update_servers(matches)

    # #####
    # Import masters into mastering database
    # #####
    images = get_masters_from_imaging(matches)

    # #####
    # Add the masters and associations masters <->entities
    # #####
    associate_masters_to_servers(images)
    # #####
    # Add the scripts
    # #####
    scripts = get_scripts_from_imaging(matches)
    for script in scripts:
        match = re.search(r"CopySysprep (.+\.xml)\n", script["value"])
        parameters = None
        if match is not None:
            parameters = get_meta_from_sysprep(match.group(1))
            if parameters is not None:
                script["value"] = script["value"].replace("%s"%match.group(1), "@@@filename@@@")
                param_script = "Win"
                _match = re.search(r"(Windows) (\d+) \[[\w]+ (uefi)|(oem)\]", parameters["os"])
                param_script += "%s-%s"%( _match.group(2), _match.group(3))
                
                parameters["meta"]["script"] = param_script
                parameters["meta"]["type"] = "sysprep"
                parameters["meta"]["mode"] = "edit"

        # Check if a script(name, entity_id) already exists
        insert_script(script, parameters)

