# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import datetime
import time
import pytz
import json
import os
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.kiosk import KioskDatabase
from pulse2.database.msc import MscDatabase
from managepackage import managepackage
import logging
from mmc.plugins.xmppmaster.master.lib.utils import (
    name_random,
    file_put_contents,
    file_get_contents,
    utc2local,
)
import re
from mmc.plugins.kiosk import handlerkioskpresence
from mmc.plugins.pkgs import get_xmpp_package

logger = logging.getLogger()

plugin = {"VERSION": "1.4", "NAME": "resultkiosk", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("#################################################")
    logger.debug(plugin)
    logger.debug(json.dumps(data, indent=4))
    logger.debug("#################################################")
    if "subaction" in data:
        if data["subaction"] == "initialization":
            initialisekiosk(data, message, xmppobject)
        elif data["subaction"] == "launch":
            deploypackage(data, message, xmppobject, sessionid)
        elif data["subaction"] == "delete":
            deploypackage(data, message, xmppobject, sessionid)
        elif data["subaction"] == "install":
            deploypackage(data, message, xmppobject, sessionid)
        elif data["subaction"] == "update":
            deploypackage(data, message, xmppobject, sessionid)
        elif data["subaction"] == "presence":
            machine = XmppMasterDatabase().getMachinefromjid(message["from"])
            if "id" in machine:
                result = XmppMasterDatabase().updatemachine_kiosk_presence(
                    machine["id"], data["value"]
                )
        elif data["subaction"] == "ask":
            machine = XmppMasterDatabase().getMachinefromjid(message["from"])
            profiles = []
            if machine is not None:
                OUmachine = [
                    machine["ad_ou_machine"]
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("@@", "/")
                ]
                OUuser = [
                    machine["ad_ou_user"]
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("@@", "/")
                ]
                OU = [elem for elem in set(OUmachine + OUuser) if elem != ""]
                profiles = KioskDatabase().add_askacknowledge(
                    OU, data["uuid"], data["askuser"]
                )
        else:
            print("No subaction found")
    else:
        pass


def parsexmppjsonfile(path):
    datastr = file_get_contents(path)

    datastr = re.sub(r"(?i) *: *false", " : false", datastr)
    datastr = re.sub(r"(?i) *: *true", " : true", datastr)

    file_put_contents(path, datastr)


def initialisekiosk(data, message, xmppobject):
    machine = XmppMasterDatabase().getMachinefromjid(message["from"])
    if "userlist" and "oumachine" and "ouuser" in data:
        if len(data["userlist"]) == 0:
            user = ""
        else:
            user = data["userlist"][0]
        print("call updatemachineAD")
        XmppMasterDatabase().updatemachineAD(
            machine["id"], user, data["oumachine"], data["ouuser"]
        )

    initializationdatakiosk = handlerkioskpresence(
        message["from"],
        machine["id"],
        machine["platform"],
        machine["hostname"],
        machine["uuid_inventorymachine"],
        machine["agenttype"],
        classutil=machine["classutil"],
        fromplugin=True,
    )

    datasend = {
        "sessionid": name_random(6, "initialisation_kiosk"),
        "action": "kiosk",
        "data": initializationdatakiosk,
    }
    xmppobject.send_message(
        mto=message["from"], mbody=json.dumps(datasend), mtype="chat"
    )


def deploypackage(data, message, xmppobject, sessionid):
    machine = XmppMasterDatabase().getMachinefromjid(message["from"])

    # Get the actual timestamp in utc format
    current_date = datetime.datetime.utcnow()
    current_date = current_date.replace(tzinfo=pytz.UTC)
    section = ""

    if "utcdatetime" in data:
        date_str = data["utcdatetime"].replace("(", "")
        date_str = date_str.replace(")", "")
        date_list_tmp = date_str.split(",")
        date_list = []
        for element in date_list_tmp:
            date_list.append(int(element))

        sent_datetime = datetime.datetime(
            date_list[0],
            date_list[1],
            date_list[2],
            date_list[3],
            date_list[4],
            0,
            0,
            pytz.UTC,
        )
        install_date = utc2local(sent_datetime)
    else:
        install_date = current_date

    nameuser = "(kiosk):%s/%s" % (machine["lastuser"], machine["hostname"])
    if data["subaction"] == "install":
        section = '"section":"install"'
    elif data["subaction"] == "delete":
        section = '"section":"uninstall"'
    elif data["subaction"] == "update":
        section = '"section":"update"'
    else:
        section = '"section":"install"'

    package = json.loads(get_xmpp_package(data["uuid"]))
    _section = section.split(":")[1]
    command = MscDatabase().createcommanddirectxmpp(
        data["uuid"],
        "",
        section,
        "malistetodolistfiles",
        "enable",
        "enable",
        install_date,
        install_date + datetime.timedelta(hours=1),
        nameuser,
        nameuser,
        package["info"]["name"] + " : " + _section,
        60,
        4,
        0,
        "",
        None,
        None,
        None,
        "none",
        "active",
        "1",
        cmd_type=0,
    )
    commandid = command.id
    commandstart = command.start_date
    commandstop = command.end_date
    jidrelay = machine["groupdeploy"]
    uuidmachine = machine["uuid_inventorymachine"]
    jidmachine = machine["jid"]
    try:
        target = MscDatabase().xmpp_create_Target(uuidmachine, machine["hostname"])

    except Exception as e:
        traceback.print_exc(file=sys.stdout)

    idtarget = target["id"]

    MscDatabase().xmpp_create_CommandsOnHost(
        commandid, idtarget, machine["hostname"], commandstop, commandstart
    )

    # Write advanced parameter for the deployment
    XmppMasterDatabase().addlogincommand(
        nameuser, commandid, "", "", "", "", section, 0, 0, 0, 0, {}
    )

    sessionid = name_random(5, "deploykiosk_")
    name = managepackage.getnamepackagefromuuidpackage(data["uuid"])

    path = managepackage.getpathpackagename(name)

    descript = managepackage.loadjsonfile(os.path.join(path, "xmppdeploy.json"))
    parsexmppjsonfile(os.path.join(path, "xmppdeploy.json"))
    if descript is None:
        logger.error(
            "deploy %s on %s  error : xmppdeploy.json missing"
            % (data["uuid"], machine["hostname"])
        )
        return None
    objdeployadvanced = XmppMasterDatabase().datacmddeploy(commandid)
    if not objdeployadvanced:
        logger.error(
            "The line has_login_command for the idcommand %s is missing" % commandid
        )
        logger.error("To solve this, please remove the group, and recreate it")
    datasend = {
        "name": name,
        "login": nameuser,
        "idcmd": commandid,
        "advanced": objdeployadvanced,
        "methodetransfert": "pushrsync",
        "path": path,
        "packagefile": os.listdir(path),
        "jidrelay": jidrelay,
        "jidmachine": jidmachine,
        "jidmaster": xmppobject.boundjid.bare,
        "iprelay": XmppMasterDatabase().ipserverARS(jidrelay)[0],
        "ippackageserver": XmppMasterDatabase().ippackageserver(jidrelay)[0],
        "portpackageserver": XmppMasterDatabase().portpackageserver(jidrelay)[0],
        "ipmachine": XmppMasterDatabase().ipfromjid(jidmachine)[0],
        "ipmaster": xmppobject.config.Server,
        "Dtypequery": "TQ",
        "Devent": "DEPLOYMENT START",
        "uuid": uuidmachine,
        "descriptor": descript,
        "transfert": True,
    }
    # run deploy

    sessionid = xmppobject.send_session_command(
        jidrelay,
        "applicationdeploymentjson",
        datasend,
        datasession=None,
        encodebase64=False,
    )
    # add deploy in table.
    XmppMasterDatabase().adddeploy(
        commandid,
        machine["jid"],  # jidmachine
        machine["groupdeploy"],  # jidrelay,
        machine["hostname"],  # host,
        machine["uuid_inventorymachine"],  # inventoryuuid,
        data["uuid"],  # uuidpackage,
        "DEPLOYMENT START",  # state,
        sessionid,  # id session,
        nameuser,  # user
        nameuser,  # login
        name + " " + commandstart.strftime("%Y/%m/%d/ %H:%M:%S"),  # title,
        "",  # group_uuid
        commandstart,  # startcmd
        commandstop,  # endcmd
        machine["macaddress"],
    )

    # Convert install_date to timestamp and send it to logs
    timestamp_install_date = int(time.mktime(install_date.timetuple()))
    xmppobject.xmpplog(
        "Start deploy on machine %s" % jidmachine,
        type="deploy",
        sessionname=sessionid,
        priority=-1,
        action="",
        who=nameuser,
        how="",
        why=xmppobject.boundjid.bare,
        module="Deployment | Start | Creation",
        date=timestamp_install_date,
        fromuser=nameuser,
        touser="",
    )
