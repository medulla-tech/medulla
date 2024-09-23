# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Plugin to manage the interface with xmppmaster
"""

import logging
import os
import re
from mmc.plugins.xmppmaster.config import xmppMasterConfig
from .master.lib.managepackage import apimanagepackagemsc
from pulse2.version import getVersion, getRevision  # pyflakes.ignore
import hashlib
import json

# Database
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.msc.database import MscDatabase
from pulse2.database.pkgs import PkgsDatabase
from pulse2.utils import xmlrpcCleanup

import zlib
import base64
from .master.lib.utils import name_random, file_get_contents
from .xmppmaster import *
from mmc.plugins.xmppmaster.master.agentmaster import (
    XmppSimpleCommand,
    getXmppConfiguration,
    callXmppFunction,
    ObjectXmpp,
    callXmppPlugin,
    callInventory,
    callrestartbymaster,
    callrestartbotbymaster,
    callshutdownbymaster,
    send_message_json,
    callvncchangepermsbymaster,
    callInstallKey,
    callremotefile,
    calllocalfile,
    callremotecommandshell,
    calllistremotefileedit,
    callremotefileeditaction,
    callremoteXmppMonitoring,
)
from .master.lib.manage_grafana import manage_grafana

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = xmppMasterConfig("xmppmaster")
    if config.disable:
        logger.warning("Plugin xmppmaster: disabled by configuration.")
        return False
    if not XmppMasterDatabase().activate(config):
        logger.warning(
            "Plugin XmppMaster: an error occurred during the database initialization"
        )
        return False
    return True


# #############################################################
# xmppmaster MAIN FUNCTIONS [HTTP INTERFACE]
# #############################################################


def getlinelogssession(sessionxmpp):
    return XmppMasterDatabase().getlinelogssession(sessionxmpp)


def getListPackages():
    resultnamepackage = []
    FichList = [
        f
        for f in os.listdir("/var/lib/pulse2/packages/")
        if os.path.isfile(
            os.path.join("/var/lib/pulse2/packages/", f, "xmppdeploy.json")
        )
    ]
    for package in FichList:
        with open(
            os.path.join("/var/lib/pulse2/packages/", package, "xmppdeploy.json"), "r"
        ) as fichier:
            session = json.load(fichier)
            resultnamepackage.append(session["info"]["name"])
    return resultnamepackage


def set_simple_log(textinfo, sessionxmppmessage, typelog, priority, who):
    return XmppMasterDatabase().logtext(
        textinfo,
        sessionname=sessionxmppmessage,
        type=typelog,
        priority=priority,
        who=who,
    )


def updatedeploystate(sessionxmppmessage, status):
    return XmppMasterDatabase().updatedeploystate(sessionxmppmessage, status)


def adddeployabort(
    idcommand,
    jidmachine,
    jidrelay,
    host,
    inventoryuuid,
    uuidpackage,
    state,
    sessionid,
    user,
    login,
    title,
    group_uuid,
    startcmd,
    endcmd,
    macadress,
):
    return XmppMasterDatabase().adddeploy(
        idcommand,
        jidmachine,
        jidrelay,
        host,
        inventoryuuid,
        uuidpackage,
        state,
        sessionid,
        user,
        login,
        title,
        group_uuid,
        startcmd,
        endcmd,
        macadress,
    )


def updatedeploystate1(sessionxmppmessage, status):
    return XmppMasterDatabase().updatedeploystate1(sessionxmppmessage, status)


def getstepdeployinsession(sessionname):
    return XmppMasterDatabase().getstepdeployinsession(sessionname)


def delMachineXmppPresence(uuidinventory):
    return XmppMasterDatabase().delMachineXmppPresence(uuidinventory)


def setlogxmpp(
    text, type, sessionname, priority, who, how, why, module, action, touser, fromuser
):
    if sessionname.startswith("update"):
        type = "update"
    return XmppMasterDatabase().setlogxmpp(
        text,
        type,
        sessionname,
        priority,
        who,
        how,
        why,
        module,
        action,
        touser,
        fromuser,
    )


def setlogxmpp(
    text, type, sessionname, priority, who, how, why, module, action, touser, fromuser
):
    return XmppMasterDatabase().setlogxmpp(
        text,
        type,
        sessionname,
        priority,
        who,
        how,
        why,
        module,
        action,
        touser,
        fromuser,
    )


def syncthingmachineless(grp, cmd):
    return XmppMasterDatabase().syncthingmachineless(grp, cmd)


def getLogxmpp(
    start_date, end_date, typelog, action, module, user, how, who, why, headercolumn
):
    if typelog == "None" and action == "None" and module == "None" and start_date == "":
        return []
    if typelog == "None":
        typelog == ""
    if module == "None":
        module == ""
    if action == "None":
        action == ""
    return XmppMasterDatabase().getLogxmpp(
        start_date, end_date, typelog, action, module, user, how, who, why, headercolumn
    )


def get_machines_list(start, end, ctx):
    return XmppMasterDatabase().get_machines_list(start, end, ctx)


def getPresenceuuid(uuid):
    return XmppMasterDatabase().getPresenceuuid(uuid)


def getPresenceuuids(uuids):
    return XmppMasterDatabase().getPresenceuuids(uuids)


# topology


def topologypulse():
    return XmppMasterDatabase().topologypulse()


def getMachinefromjid(jid):
    return XmppMasterDatabase().getMachinefromjid(jid)


def getMachinefromuuid(uuid):
    return XmppMasterDatabase().getMachinefromuuid(uuid)


def getRelayServerfromjid(jid):
    return XmppMasterDatabase().getRelayServerfromjid(jid)


def getlistcommandforuserbyos(
    login, osname=None, min=None, max=None, filt=None, edit=None
):
    if osname == "":
        osname = None
    if min == "":
        min = None
    if max == "":
        max = None
    if filt == "":
        filt = None
    if edit == "":
        edit = None

    return XmppMasterDatabase().getlistcommandforuserbyos(
        login, osname=osname, min=min, max=max, filt=filt, edit=edit
    )


def delQa_custom_command(login, name, osname):
    return XmppMasterDatabase().delQa_custom_command(login, name, osname)


def create_Qa_custom_command(login, osname, namecmd, customcmd, description):
    return XmppMasterDatabase().create_Qa_custom_command(
        login, osname, namecmd, customcmd, description
    )


def updateName_Qa_custom_command(login, osname, namecmd, customcmd, description):
    return XmppMasterDatabase().updateName_Qa_custom_command(
        login, osname, namecmd, customcmd, description
    )


def create_local_dir_transfert(pathroot, hostname):
    dirmachine = os.path.join(pathroot, hostname)
    if not os.path.exists(dirmachine):
        os.makedirs(dirmachine)
        os.chmod(dirmachine, 0o777)
    return localfile(dirmachine)


def getGuacamoleRelayServerMachineUuid(uuid):
    return XmppMasterDatabase().getGuacamoleRelayServerMachineUuid(uuid)


def getGuacamoleRelayServerMachineHostnameProto(hostname):
    result = {
        "machine": getGuacamoleRelayServerMachineHostname(hostname),
        "proto": getGuacamoleIdForHostname(hostname),
    }
    return result


def getGuacamoleRelayServerMachineHostname(hostname):
    return XmppMasterDatabase().getGuacamoleRelayServerMachineHostname(hostname)


def getGuacamoleidforUuid(uuid):
    return XmppMasterDatabase().getGuacamoleidforUuid(uuid)


def getGuacamoleIdForHostname(hostname):
    return XmppMasterDatabase().getGuacamoleIdForHostname(hostname)


def getListPresenceAgent():
    return json.dumps(ObjectXmpp().presencedeployment, encoding="latin1")


def getListPresenceMachine():
    return XmppMasterDatabase().getListPresenceMachine()


def getCountPresenceMachine():
    return XmppMasterDatabase().getCountPresenceMachine()


def getjidMachinefromuuid(uuid):
    return XmppMasterDatabase().getjidMachinefromuuid(uuid)


def getListPresenceRelay():
    return XmppMasterDatabase().getListPresenceRelay()


def deploylog(uuidinventory, nblastline):
    return XmppMasterDatabase().deploylog(uuidinventory, nblastline)


def addlogincommand(
    login,
    commandid,
    grpid,
    nb_machine_in_grp,
    instructions_nb_machine_for_exec,
    instructions_datetime_for_exec,
    parameterspackage,
    rebootrequired,
    shutdownrequired,
    limit_rate_ko,
    syncthing,
    params,
):
    return XmppMasterDatabase().addlogincommand(
        login,
        commandid,
        grpid,
        nb_machine_in_grp,
        instructions_nb_machine_for_exec,
        instructions_datetime_for_exec,
        parameterspackage,
        rebootrequired,
        shutdownrequired,
        limit_rate_ko,
        syncthing,
        params,
    )


def loginbycommand(commandid):
    return XmppMasterDatabase().loginbycommand(commandid)


def getdeployfromcommandid(command_id, uuid):
    return XmppMasterDatabase().getdeployfromcommandid(command_id, uuid)


def getdeployment_cmd_and_title(command_id, title, search_filter="", start=0, limit=-1):
    """
    Get the list of deploys based on the command_id and title of the packages.

    Arg:
        sesion: The SQL Alchemy session
        command_id: The id the package
        title: Name of the package
        search_filter: Used filters in the web page
        start: Number of the first package to show.
        limit: Maximum number of deploys sent at once.

    Return:
        It returns the list of the deploys

    """
    return XmppMasterDatabase().getdeployment_cmd_and_title(
        command_id, title, search_filter, start, limit
    )


def getstatdeploy_from_command_id_and_title(command_id, title):
    """
    Retrieve the deploy statistics based on the command_id and name
    Args:
        session: The SQL Alchemy session
        command_id: id of the deploy
        title: The name of deploy
    Return:
        It returns the number of machines per status.
    """
    return XmppMasterDatabase().getstatdeploy_from_command_id_and_title(
        command_id, title
    )


def getdeployment(command_id, filter="", start=0, limit=-1):
    return XmppMasterDatabase().getdeployment(command_id, filter, start, limit)


def stat_syncthing_transfert(group_id, command_id):
    return XmppMasterDatabase().stat_syncthing_transfert(group_id, command_id)


def getstatdeployfromcommandidstartdate(command_id, datestart):
    return XmppMasterDatabase().getstatdeployfromcommandidstartdate(
        command_id, datestart
    )


def get_machine_stop_deploy(cmdid, uuid):
    result = XmppMasterDatabase().get_machine_stop_deploy(cmdid, uuid)
    if result:
        msg_stop_deploy = {
            "action": "enddeploy",
            "sessionid": result["sessionid"],
            "data": {"typerequest": "bansessionid"},
            "ret": 0,
            "base64": False,
        }
        updatedeploystate(result["sessionid"], "ABORT DEPLOYMENT CANCELLED BY USER")
        if "jid_relay" in result and result["jid_relay"] != "fake_jidrelay":
            send_message_json(result["jid_relay"], msg_stop_deploy)
        if "jidmachine" in result and result["jidmachine"] != "fake_jidmachine":
            send_message_json(result["jidmachine"], msg_stop_deploy)
        return True
    return False


def get_group_stop_deploy(grpid, cmdid):
    result = XmppMasterDatabase().get_group_stop_deploy(grpid, cmdid)
    msg_stop_deploy = {
        "action": "enddeploy",
        "sessionid": "",
        "data": {"typerequest": "bansessionid"},
        "ret": 0,
        "base64": False,
    }
    for machine in result["objectdeploy"]:
        msg_stop_deploy["sessionid"] = machine["sessionid"]
        updatedeploystate1(machine["sessionid"], "ABORT DEPLOYMENT CANCELLED BY USER")
        if "jidmachine" in machine and machine["jidmachine"] != "fake_jidmachine":
            send_message_json(machine["jidmachine"], msg_stop_deploy)
        if "jid_relay" in machine and machine["jid_relay"] != "fake_jidrelay":
            arscluster = XmppMasterDatabase().getRelayServerofclusterFromjidars(
                machine["jid_relay"]
            )
            for t in arscluster:
                send_message_json(t, msg_stop_deploy)
    return True


def getlinelogswolcmd(idcommand, uuid):
    return XmppMasterDatabase().getlinelogswolcmd(idcommand, uuid)


def getdeploybyuserlen(login, typedeploy="command"):
    if not login:
        login = None
    return XmppMasterDatabase().getdeploybyuserlen(login, typedeploy)


def get_deploy_for_machine(
    uuidinventory, state, intervalsearch, minimum, maximum, filt, typedeploy="command"
):
    """
    This function is used to retrieve the deploy of a user.
    Args:
        uuidinventory: The login of the user
        state: The state of the deploy. (Started, Error, etc. ).
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
    Returns:
        It returns all the deployement for a machine.
    """
    return XmppMasterDatabase().get_deploy_for_machine(
        uuidinventory, state, intervalsearch, minimum, maximum, filt, typedeploy
    )


def get_deploy_from_group(
    gid, state, intervalsearch, minimum, maximum, filt, typedeploy="command"
):
    """
    This function is used to retrieve the deploy of a machine's group.
    Args:
        session: The SQL Alchemy session
        group_uuid: The login of the user
        state: The state of the deploy. (Started, Error, etc. ).
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
    Returns:
        It returns all the deployement of a group.
    """
    return XmppMasterDatabase().get_deploy_from_group(
        gid, state, intervalsearch, minimum, maximum, filt, typedeploy
    )


def delDeploybygroup(numgrp):
    return XmppMasterDatabase().delDeploybygroup(numgrp)


def get_deploy_by_team_member(
    login,
    state,
    intervalsearch,
    minimum=None,
    maximum=None,
    filt=None,
    typedeploy="command",
):
    """
    This function is used to retrieve the deployements of a team.
    This team is found based on the login of a member.

    Args:
        session: The SQL Alchemy session
        login: The login of the user
        state: State of the deployment (Started, Error, etc.)
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
        Returns:
            It returns all the deployement done by a specific team.
            It can be done by time search too.
    """

    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    if filt == "":
        filt = None
    return XmppMasterDatabase().get_deploy_by_team_member(
        login, state, intervalsearch, minimum, maximum, filt, typedeploy
    )


def get_deploy_inprogress_by_team_member(
    login, intervalsearch, minimum=None, maximum=None, filt=None, typedeploy="command"
):
    """
    This function is used to retrieve not yet done deployements of a team.
    This team is found based on the login of a member.

    Args:
        login: The login of the user
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
        Returns:
            It returns all the deployement not yet started of a specific team.
            It can be done by time search too.
    """

    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    if filt == "":
        filt = None
    # call xmppmaster search users list of team
    pulse_usersidlist = XmppMasterDatabase().get_teammembers_from_login(login)
    # call msc search no deploy
    return MscDatabase().get_deploy_inprogress_by_team_member(
        pulse_usersidlist, intervalsearch, minimum, maximum, filt, typedeploy
    )


def get_deploy_xmpp_teamscheduler(login, minimum=None, maximum=None, filt=None):
    """
    This function is used to retrieve the depoyement from a team.
    Args:
        login: The login of the user
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
    Returns:
        It returns the deploys of a team. Defined by the login of one user of this team.
    """

    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    if filt == "":
        filt = None

    pulse_usersidlist = XmppMasterDatabase().get_teammembers_from_login(login)
    result = MscDatabase().deployxmppscheduler(
        pulse_usersidlist, minimum, maximum, filt
    )
    return result


def get_deploy_by_team_finished(
    login, intervalsearch, minimum=None, maximum=None, filt=None, typedeploy="command"
):
    """
    This function is used to retrieve all the deployments done by a team.
    Args:
        login: The login of the user
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
    Returns:
        It returns all the deployment done by a team
    """
    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    pulse_usersidlist = XmppMasterDatabase().get_teammembers_from_login(login)
    return XmppMasterDatabase().get_deploy_by_user_finished(
        pulse_usersidlist, intervalsearch, minimum, maximum, filt, typedeploy
    )


def get_deploy_by_user_with_interval(
    login,
    state,
    intervalsearch,
    minimum=None,
    maximum=None,
    filt=None,
    typedeploy="command",
):
    """
    This function is used to retrive the recent deployment done by a user.

    Args:
        login: The login of the user
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search

    Returns:
        It returns all the deployment done by a user.
        If intervalsearch is not used it is by default in the last 24 hours."""
    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    if filt == "":
        filt = None
    return XmppMasterDatabase().get_deploy_by_user_with_interval(
        login, state, intervalsearch, minimum, maximum, filt, typedeploy
    )


def get_deploy_by_user_finished(
    login, intervalsearch, minimum=None, maximum=None, filt=None, typedeploy="command"
):
    """
    This function is used to retrieve all the deployments done by a user (or a team).

    Args:
        login: The login of the user
        state: State of the deployment (Started, Error, etc.)
        intervalsearch: The interval on which we search the deploys.
        minimum: Minimum value ( for pagination )
        maximum: Maximum value ( for pagination )
        filt: Filter of the search
    Returns:
        There is 3 scenario.
            If login is empty, this returns all the past deploys for everyone
            If login is a string, this returns all the past deploys for this user
            If login is a list, this returns all the past deploys for the group this user belong to.
    """
    if minimum == "":
        minimum = None
    if maximum == "":
        maximum = None
    return XmppMasterDatabase().get_deploy_by_user_finished(
        login, intervalsearch, minimum, maximum, filt, typedeploy
    )


def getdeploybyuser(login, numrow, offset, typedeploy="command"):
    if not numrow:
        numrow = None
    if not offset:
        offset = None
    return XmppMasterDatabase().getdeploybyuser(login, numrow, offset, typedeploy)


def getshowmachinegrouprelayserver():
    def Nonevalue(x):
        if x == None:
            return ""
        else:
            return x

    machinelist = XmppMasterDatabase().showmachinegrouprelayserver()
    array = []
    for t in machinelist:
        z = [Nonevalue(x) for x in list(t)]
        ob = {
            "jid": z[0],
            "type": z[1],
            "os": z[2],
            "rsdeploy": z[3],
            "hostname": z[4],
            "uuid": z[5],
            "ip": z[6],
            "subnet": z[7],
        }
        array.append(ob)
    return array


def get_qaction(groupname, user, grp, completename):
    return XmppMasterDatabase().get_qaction(groupname, user, grp, completename)


def setCommand_qa(
    command_name,
    command_action,
    command_login,
    command_grp="",
    command_machine="",
    command_os="",
    jid="",
):
    return XmppMasterDatabase().setCommand_qa(
        command_name,
        command_action,
        command_login,
        command_grp,
        command_machine,
        command_os,
        jid,
    )


def getCommand_action_time(during_the_last_seconds, start, stop, filt):
    return XmppMasterDatabase().getCommand_action_time(
        during_the_last_seconds, start, stop, filt
    )


def setCommand_action(
    target, command_id, sessionid, command_result, typemessage, jid=""
):
    return XmppMasterDatabase().setCommand_action(
        target, command_id, sessionid, command_result, typemessage, jid
    )


def getCommand_qa_by_cmdid(cmdid):
    return XmppMasterDatabase().getCommand_qa_by_cmdid(cmdid)


def getQAforMachine(cmd_id, uuidmachine):
    resultdata = XmppMasterDatabase().getQAforMachine(cmd_id, uuidmachine)
    if resultdata[0][3] == "result":
        # encode 64 str? to transfer xmlrpc if string with sequence escape
        resultdata[0][4] = base64.b64encode(resultdata[0][4].encode("utf-8"))
    return resultdata


def getQAforMachineByJid(cmd_id, jid):
    resultdata = XmppMasterDatabase().getQAforMachineByJid(cmd_id, jid)
    if resultdata[0][3] == "result":
        # encode 64 str? to transfer xmlrpc if string with sequence escape
        resultdata[0][4] = base64.b64encode(resultdata[0][4])
    return resultdata


def runXmppApplicationDeployment(*args, **kwargs):
    for count, thing in enumerate(args):
        print("{0}. {1}".format(count, thing))
    for name, value in list(kwargs.items()):
        print("{0} = {1}".format(name, value))
    return callXmppFunction(*args, **kwargs)


def CallXmppPlugin(*args, **kwargs):
    return callXmppPlugin(*args, **kwargs)


def callInventoryinterface(uuid):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callInventory(jid)
        return jid
    else:
        logging.getLogger().error("for machine %s : jid xmpp missing" % uuid)
        return "jid missing"


def callrestartbot(uuid):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callrestartbotbymaster(jid)
        return jid
    else:
        logging.getLogger().error(
            "call restart bot for machine %s : jid xmpp missing" % uuid
        )
        return "jid missing"


def callrestartbothostname(hostname):
    """
    This function is used to restart a computer based on the hostname.
    Args:
        hostname: The hostname of the machine we want to restart.
    """
    machine = XmppMasterDatabase().get_machine_from_hostname(hostname)
    if machine:
        if len(machine) > 1:
            logging.getLogger().warning(
                "Several Machine have the same hostname %s in the xmppmaster SQL database"
                % hostname
            )
        else:
            if machine[0]["jid"]:
                logging.getLogger().debug(
                    "Restarting the agent for the machine %s" % hostname
                )
                callrestartbotbymaster(machine[0]["jid"])
            else:
                logging.getLogger().error(
                    "The machine %s has not been found in the xmppmaster SQL database."
                    % hostname
                )
                logging.getLogger().error("Please check the logs in the client machine")


def createdirectoryuser(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, 0o777)
        return True
    return False


def callInstallKeyAM(jidAM, jidARS):
    if jidARS != "" and jidAM != "":
        callInstallKey(jidAM, jidARS)
        return jidAM
    else:
        logging.getLogger().error(
            "for machine %s : install key ARS %s" % (jidAM, jidARS)
        )
        return "jid (AM or ARS) missing"


def callrestart(uuid, jid_type=False):
    if jid_type is False:
        jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    else:
        jid = uuid
    if jid != "":
        callrestartbymaster(jid)
        return jid
    else:
        logging.getLogger().error(
            "callrestartbymaster for machine %s : jid xmpp missing" % uuid
        )
        return "jid missing"


def callshutdown(uuid, time, msg):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callshutdownbymaster(jid, time, msg)
        return jid
    else:
        logging.getLogger().error(
            "callshutdownbymaster for machine %s : jid xmpp missing" % uuid
        )
        return "jid missing"


def callvncchangeperms(uuid, askpermission):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callvncchangepermsbymaster(jid, askpermission)
        return jid
    else:
        logging.getLogger().error(
            "callvncchangepermsbymaster for machine %s : jid xmpp missing" % uuid
        )
        return "jid missing"


def localfile(currentdir):
    return calllocalfile(currentdir)


def remotefile(currentdir, jidmachine):
    return callremotefile(jidmachine, currentdir)


def listremotefileedit(jidmachine):
    aa = calllistremotefileedit(jidmachine)
    objout = json.loads(aa)
    print(objout["data"]["result"])
    return objout["data"]["result"]


def remotefileeditaction(jidmachine, data):
    resultjsonstr = callremotefileeditaction(jidmachine, data)
    if not isinstance(resultjsonstr, str):
        return resultjsonstr
    objout = json.loads(resultjsonstr)
    if "data" in objout:
        return objout["data"]
    return objout


def getcontentfile(pathfile, deletefile):
    if os.path.isfile(pathfile):
        data = file_get_contents(pathfile)
        if deletefile == True:
            os.remove(pathfile)
        return data
    else:
        return False


def remotecommandshell(command, jidmachine, timeout):
    return callremotecommandshell(jidmachine, command, timeout=timeout)


def remoteXmppMonitoring(subject, jidmachine, timeout):
    data = callremoteXmppMonitoring(jidmachine, subject, timeout=timeout)
    result = json.loads(data)
    resultdata = zlib.decompress(base64.b64decode(result["result"]))
    resultdata_str = resultdata.decode("utf-8")
    dataresult = [x for x in resultdata_str.split("\n")]
    result["result"] = dataresult
    return result


def runXmppAsyncCommand(cmd, infomachine):
    sessionid = name_random(8, "quick_")
    cmd = cmd.strip()
    if cmd.startswith("plugin_"):
        # call plugin master
        lineplugincalling = [x.strip() for x in cmd.split("@_@")]
        plugincalling = lineplugincalling[0]
        del lineplugincalling[0]
        action = plugincalling.strip().split("_")
        action.pop(0)
        action = "_".join(action)
        data = {
            "action": action,
            "sessionid": sessionid,
            "data": [infomachine["jid"], infomachine, lineplugincalling],
        }
        XmppMasterDatabase().setCommand_action(
            infomachine["uuid_inventorymachine"],
            infomachine["cmdid"],
            sessionid,
            "call plugin %s for Quick Action" % (action),
            "log",
        )
        callXmppPlugin(action, data)
    else:
        data = {
            "action": "asynchroremoteQA",
            "sessionid": sessionid,
            "data": infomachine,
            "base64": False,
        }
        callXmppPlugin("asynchroremoteQA", data)


def runXmppCommand(cmd, machine, information=""):
    data = {
        "action": "cmd",
        "sessionid": name_random(8, "quick_"),
        "data": [machine, information],
        "base64": False,
    }
    cmd = cmd.strip()
    if cmd.startswith("plugin_"):
        # call plugin master
        lineplugincalling = [x.strip() for x in cmd.split("@_@")]
        plugincalling = lineplugincalling[0]
        del lineplugincalling[0]
        action = plugincalling.strip().split("_")[1]
        data = {
            "action": action,
            "sessionid": name_random(8, "quick_"),
            "data": [machine, information, lineplugincalling],
            "base64": False,
        }
        callXmppPlugin(action, data)
        return {
            "action": "resultshellcommand",
            "sessionid": "mcc_221n4h6h",
            "base64": False,
            "data": {"result": "call plugin : %s to machine : %s" % (action, machine)},
            "ret": 0,
        }
    else:
        data = {
            "action": "shellcommand",
            "sessionid": name_random(8, "mcc_"),
            "data": {"cmd": cmd},
            "base64": False,
        }
        a = XmppSimpleCommand(machine, data, 70)
        d = a.t2.join()
        print(type(a.result))
    return a.result


def runXmppScript(cmd, machine):
    data = {
        "action": "shellcommand",
        "sessionid": name_random(8, "mcc_"),
        "data": {"cmd": cmd},
        "base64": False,
    }
    a = XmppSimpleCommand(machine, data, 70)
    d = a.t2.join()
    return a.result


def getCountOnlineMachine():
    return XmppMasterDatabase().getCountOnlineMachine()


############### package #####################
def xmppGetAllPackages(login, filter, start, end):
    return apimanagepackagemsc.loadpackagelistmsc(login, filter, start, end)


def xmpp_getPackageDetail(pid_package):
    return apimanagepackagemsc.getPackageDetail(pid_package)


def runXmppWolforuuidsarray(uuids):
    """
    renvoi les informations wol network
    """
    if isinstance(uuids, dict) and "jid" in uuids:
        mach_infos = XmppMasterDatabase().getMacsMachinefromjid(str(uuids["jid"]))
    elif isinstance(uuids, list):
        mach_infos = XmppMasterDatabase().getMacsMachinefromjid(uuids)
    else:
        return False
    if mach_infos is None:
        return False
    macaddresslist = []
    broadcastlist = []
    groupdeploylist = []
    for element in mach_infos:
        macaddresslist.append(element["macaddress"])
        broadcastlist.append(element["broadcast"])
        groupdeploylist.append(element["groupdeploy"].split("/")[0])
    callXmppPlugin(
        "wakeonlangroup",
        {
            "macadress": macaddresslist,
            "broadcast": broadcastlist,
            "groupdeploy": groupdeploylist,
        },
    )
    return True


############### synchro syncthing package #####################


def pkgs_delete_synchro_package(uuidpackage):
    return PkgsDatabase().pkgs_delete_synchro_package(uuidpackage)


# def xmpp_delete_synchro_package(uuidpackage):
# return XmppMasterDatabase().xmpp_delete_synchro_package(uuidpackage)


def xmpp_get_info_synchro_packageid(uuidpackage):
    list_relayservernosync = (
        XmppMasterDatabase().get_relayservers_no_sync_for_packageuuid(uuidpackage)
    )
    list_relayserver = XmppMasterDatabase().getRelayServer(enable=True)
    return [list_relayservernosync, list_relayserver]


def get_agent_descriptor_base():
    # Sending IQ request and data reception
    data = ObjectXmpp().iqsendpulse(
        "rspulse@pulse/mainrelay",
        {"action": "remotexmppmonitoring", "data": "agentinfos"},
        300,
    )

    result = json.loads(data)

    if "result" in result:
        resultdata = zlib.decompress(base64.b64decode(result["result"]))
        resultdata_str = resultdata.decode("utf-8")
        resultdata = json.loads(resultdata_str)

        logger.error(
            "Voilà resultdata dans get_agent_descriptor_base %s" % str(resultdata)
        )

        agent_descriptor = resultdata.get("agentdescriptor", "{}")
        pathagent = resultdata.get("pathagent", "")

        if isinstance(agent_descriptor, str):
            agent_descriptor = json.loads(agent_descriptor)

        lib_agent_sorted = {
            k: agent_descriptor["lib_agent"][k]
            for k in sorted(
                agent_descriptor.get("lib_agent", {}),
                key=lambda x: (x.startswith("__"), x),
            )
        }

        new_structure = {
            "autoupdate": True,
            "directory": {
                "program_agent": agent_descriptor.get("program_agent", {}),
                "version": agent_descriptor.get("version", ""),
                "version_agent": agent_descriptor.get("version_agent", ""),
                "lib_agent": lib_agent_sorted,
                "script_agent": agent_descriptor.get("script_agent", {}),
                "fingerprint": agent_descriptor.get("fingerprint", ""),
            },
            "dir_agent_base": pathagent,
        }

        return new_structure
    else:
        logger.error(
            "The 'Result' key is missing in the result. Check the logs of the agent."
        )
        return {}


def get_plugin_lists():
    base_plugin_path = os.path.join("/", "var", "lib", "pulse2", "xmpp_baseplugin")
    files = []
    _files = []
    plugins = {}
    for _, dir, _files in os.walk(base_plugin_path):
        if dir != "__pycache__":
            # remove "plugin_" and ".py" from the name
            files = [file[7:-3] for file in _files if file.endswith(".py")]
            break

    for file in files:
        meta = {}

        with open(
            os.path.join(base_plugin_path, "plugin_%s.py" % file), "r"
        ) as plugin_fb:
            line = ""
            while line.startswith("plugin = ") is False:
                line = plugin_fb.readline()
                line = line.split("#")[0]
            try:
                meta = json.loads(line.replace("plugin =", ""))
            except Exception as error_loading:
                logger.error(f"The file {file} is not loaded correctly")
                logger.error(error_loading)
                pass
            plugins[file] = [
                meta["VERSION"],
                meta["TYPE"],
                meta["VERSIONAGENT"] if "VERSIONAGENT" in meta else "0.0.0",
            ]
            plugin_fb.close()

    base_pluginscheduler_path = os.path.join(
        "/", "var", "lib", "pulse2", "xmpp_basepluginscheduler"
    )
    pluginsscheduled = {}
    for _, dir, _files in os.walk(base_pluginscheduler_path):
        if dir != "__pycache__":
            # remove "plugin_" and ".py" from the name
            files = [file[0:-3] for file in _files if file.endswith(".py")]
            break

    for file in files:
        meta = {}
        with open(
            os.path.join(base_pluginscheduler_path, "%s.py" % file), "r"
        ) as plugin_fb:
            line = ""
            while line.startswith("plugin = ") is False:
                line = plugin_fb.readline()
                line = line.split("#")[0]
            try:
                meta = json.loads(line.replace("plugin = ", ""))
            except Exception as e:
                meta = eval(line.replace("plugin = ", ""))

            pluginsscheduled[file] = meta["VERSION"]
            plugin_fb.close()

    # Sorting of plugins in alphabetical order
    sorted_base_plugins = {
        k: plugins[k] for k in sorted(plugins, key=lambda x: (x.startswith("__"), x))
    }
    sorted_pluginsscheduled = {k: pluginsscheduled[k] for k in sorted(pluginsscheduled)}

    return [sorted_base_plugins, sorted_pluginsscheduled, base_plugin_path]


def get_conf_master_agent():
    rest = {}
    conf = dict(getXmppConfiguration())
    for t in conf:
        if t in ["passwordconnection", "dbpasswd", "confpasswordmuc"]:
            continue
        if isinstance(conf[t], (dict, list, tuple, int, str)):
            rest[t] = conf[t]
    return json.dumps(rest, indent=4)


def get_list_of_users_for_shared_qa(namecmd):
    return XmppMasterDatabase().get_list_of_users_for_shared_qa(namecmd)


def delcomputer(uuid, hostname=""):
    if uuid not in [None, ""]:
        callrestartbot(uuid)
        return XmppMasterDatabase().delMachineXmppPresence(uuid)
    else:
        callrestartbothostname(hostname)
        return XmppMasterDatabase().delMachineXmppPresenceHostname(hostname)


def get_log_status():
    return XmppMasterDatabase().get_log_status()


def get_xmppmachines_list(start, limit, filter, presence):
    return XmppMasterDatabase().get_xmppmachines_list(start, limit, filter, presence)


def get_xmpprelays_list(start, limit, filter, presence):
    return XmppMasterDatabase().get_xmpprelays_list(start, limit, filter, presence)


def get_list_ars_from_sharing(sharings, start, limit, userlogin, filter):
    listidars = []
    arslistextend = []
    objsearch = {}
    if userlogin != "":
        objsearch["login"] = userlogin
        arslistextend = PkgsDatabase().pkgs_search_ars_list_from_cluster_rules(
            objsearch
        )
        # on utilise la table rules global pour etendre ou diminuer les droits d'admins sur les ars.

    for share in sharings:
        if "r" in share["permission"]:
            listidars.append(share["ars_id"])
    if arslistextend:
        listidars.extend([x[0] for x in arslistextend])
    ars_list = {}
    ars_list = XmppMasterDatabase().get_ars_list_belongs_cluster(
        listidars, start, limit, filter
    )
    if not ars_list or ars_list["count"] == 0:
        res = {"total": 0, "datas": {}, "partielcount": 0}
        return res

    stat_ars_machine = XmppMasterDatabase().get_stat_ars_machine(ars_list["jid"])
    ars_list["total_machines"] = []
    ars_list["uninventoried"] = []
    ars_list["publicclass"] = []
    ars_list["nblinuxmachine"] = []
    ars_list["inventoried_online"] = []
    ars_list["mach_on"] = []
    ars_list["uninventoried_online"] = []
    ars_list["nbmachinereconf"] = []
    ars_list["kioskon"] = []
    ars_list["inventoried"] = []
    ars_list["nbdarwin"] = []
    ars_list["kioskoff"] = []
    ars_list["bothclass"] = []
    ars_list["privateclass"] = []
    ars_list["mach_off"] = []
    ars_list["inventoried_offline"] = []
    ars_list["with_uuid_serial"] = []
    ars_list["nb_OU_mach"] = []
    ars_list["uninventoried_offline"] = []
    ars_list["nbwindows"] = []
    ars_list["nb_ou_user"] = []
    for jid in ars_list["jid"]:
        if jid in stat_ars_machine:
            ars_list["total_machines"].append(stat_ars_machine[jid]["nbmachine"])
            ars_list["uninventoried"].append(stat_ars_machine[jid]["uninventoried"])
            ars_list["publicclass"].append(stat_ars_machine[jid]["publicclass"])
            ars_list["nblinuxmachine"].append(stat_ars_machine[jid]["nblinuxmachine"])
            ars_list["inventoried_online"].append(
                stat_ars_machine[jid]["inventoried_online"]
            )
            ars_list["mach_on"].append(stat_ars_machine[jid]["mach_on"])
            ars_list["uninventoried_online"].append(
                stat_ars_machine[jid]["uninventoried_online"]
            )
            ars_list["nbmachinereconf"].append(stat_ars_machine[jid]["nbmachinereconf"])
            ars_list["kioskon"].append(stat_ars_machine[jid]["kioskon"])
            ars_list["inventoried"].append(stat_ars_machine[jid]["inventoried"])
            ars_list["nbdarwin"].append(stat_ars_machine[jid]["nbdarwin"])
            ars_list["kioskoff"].append(stat_ars_machine[jid]["kioskoff"])
            ars_list["bothclass"].append(stat_ars_machine[jid]["bothclass"])
            ars_list["privateclass"].append(stat_ars_machine[jid]["privateclass"])
            ars_list["mach_off"].append(stat_ars_machine[jid]["mach_off"])
            ars_list["inventoried_offline"].append(
                stat_ars_machine[jid]["inventoried_offline"]
            )
            ars_list["with_uuid_serial"].append(
                stat_ars_machine[jid]["with_uuid_serial"]
            )
            ars_list["nb_OU_mach"].append(stat_ars_machine[jid]["nb_OU_mach"])
            ars_list["uninventoried_offline"].append(
                stat_ars_machine[jid]["uninventoried_offline"]
            )
            ars_list["nbwindows"].append(stat_ars_machine[jid]["nbwindows"])
            ars_list["nb_ou_user"].append(stat_ars_machine[jid]["nb_ou_user"])
        else:
            ars_list["total_machines"].append(0)
            ars_list["uninventoried"].append(0)
            ars_list["publicclass"].append(0)
            ars_list["nblinuxmachine"].append(0)
            ars_list["inventoried_online"].append(0)
            ars_list["mach_on"].append(0)
            ars_list["uninventoried_online"].append(0)
            ars_list["nbmachinereconf"].append(0)
            ars_list["kioskon"].append(0)
            ars_list["inventoried"].append(0)
            ars_list["nbdarwin"].append(0)
            ars_list["kioskoff"].append(0)
            ars_list["bothclass"].append(0)
            ars_list["privateclass"].append(0)
            ars_list["mach_off"].append(0)
            ars_list["inventoried_offline"].append(0)
            ars_list["with_uuid_serial"].append(0)
            ars_list["nb_OU_mach"].append(0)
            ars_list["uninventoried_offline"].append(0)
            ars_list["nbwindows"].append(0)
            ars_list["nb_ou_user"].append(0)

    res = {
        "total": ars_list["count"],
        "datas": ars_list,
        "partielcount": len(ars_list["jid"]),
    }
    return res


def get_clusters_list(start, limit, filter):
    return XmppMasterDatabase().get_clusters_list(start, limit, filter)


def change_relay_switch(jid, switch, propagate):
    return XmppMasterDatabase().change_relay_switch(jid, switch, propagate)


def is_relay_online(jid):
    return XmppMasterDatabase().is_relay_online(jid)


def get_qa_for_relays(login=""):
    return XmppMasterDatabase().get_qa_for_relays(login)


def get_relay_qa(login, qa_relay_id):
    return XmppMasterDatabase().get_relay_qa(login, qa_relay_id)


def add_command_relay_qa(qa_relay_id, jid, login):
    qa = get_relay_qa(login, qa_relay_id)
    if qa is not None:
        command_creation = XmppMasterDatabase().add_qa_relay_launched(
            qa_relay_id, jid, login, "", []
        )
        return {"command": qa, "launched": command_creation}
    else:
        return None


def get_qa_relay_result(result_id):
    result = XmppMasterDatabase().get_qa_relay_result(result_id)
    return result


def add_qa_relay_launched(qa_relay_id, login, cluster_id, jid):
    result = XmppMasterDatabase().add_qa_relay_launched(
        qa_relay_id, login, cluster_id, jid
    )
    return result


def add_qa_relay_result(jid, exec_date, qa_relay_id, launched_id, session_id=""):
    result = XmppMasterDatabase().add_qa_relay_result(
        jid, exec_date, qa_relay_id, launched_id, session_id
    )
    return result


def get_relay_qa_launched(jid, login, start, maxperpage):
    result = XmppMasterDatabase().get_relay_qa_launched(jid, login, start, maxperpage)
    return result


def create_reverse_ssh_from_am_to_ars(
    jidmachine, remoteport, proxyport=None, ssh_port_machine=22, uninterrupted=False
):
    """
    this function creates a reverse ssh
    The machine exports its "remoteport" port on its ARS
    The port on the ARS to reach the machine local port is proxyport
    If proxyport is not defined, the ARS will be asked to suggest a free port
    The function returns the proxy port
    """
    timeout = 15
    # ssh_port_machine = 22
    machine = XmppMasterDatabase().getMachinefromjid(jidmachine)
    if machine:
        ipARS = XmppMasterDatabase().ippackageserver(machine["groupdeploy"])[0]
    else:
        return -1
    jidARS = machine["groupdeploy"]
    jidAM = jidmachine
    ipAM = machine["ip_xmpp"]

    # logging.getLogger().error("machine %s " % machine)
    # logging.getLogger().error("jidARS %s " % machine['groupdeploy'])
    # logging.getLogger().error("jidAM %s " %jidmachine)
    type_reverse = "R"
    logging.getLogger().debug("proxyport %s " % proxyport)
    iqcomand = {
        "action": "information",
        "data": {
            "listinformation": [
                "get_ars_key_id_rsa_pub",
                "get_ars_key_id_rsa",
                "get_free_tcp_port",
                "clean_reverse_ssh",
            ],
            "param": {},
        },
    }
    logging.getLogger().debug("iq to %s iqcommand is : %s " % (jidARS, iqcomand))
    result = ObjectXmpp().iqsendpulse(jidARS, iqcomand, timeout)

    res = json.loads(result)

    logging.getLogger().debug("result iqcommand : %s" % json.dumps(res, indent=4))
    if res["numerror"] != 0:
        logger.error(
            "iq information error to %s on get_ars_key_id_rsa_pub, get_ars_key_id_rsa ,get_free_tcp_port"
            % jidARS
        )
        logger.error("abandon reverse ssh")
        return

    resultatinformation = res["result"]["informationresult"]
    if proxyport is None or proxyport == 0 or proxyport == "":
        proxyportars = resultatinformation["get_free_tcp_port"]
    else:
        proxyportars = proxyport
    if not uninterrupted:
        uninterruptedstruct = {
            "action": "information",
            "data": {
                "listinformation": ["add_proxy_port_reverse"],
                "param": {"proxyport": proxyportars},
            },
        }
        logging.getLogger().debug(
            "send iqcommand to %s : %s" % (jidARS, uninterruptedstruct)
        )
        result = ObjectXmpp().iqsendpulse(jidARS, uninterruptedstruct, timeout)

        logging.getLogger().debug("result iqcommand : %s" % result)

    boundjidbare = "master@pulse/MASTER"
    structreverse = {
        "action": "reversesshqa",
        "sessionid": name_random(8, "reversshiq"),
        "from": boundjidbare,
        "data": {
            "ipARS": ipARS,
            "jidARS": jidARS,
            "jidAM": jidAM,
            "ipAM": ipAM,
            "remoteport": remoteport,
            "portproxy": proxyportars,
            "type_reverse": type_reverse,
            "port_ssh_ars": ssh_port_machine,
            "private_key_ars": resultatinformation["get_ars_key_id_rsa"],
            "public_key_ars": resultatinformation["get_ars_key_id_rsa_pub"],
        },
    }
    # structreverse = {
    # "action": "reversesshqa",
    # "sessionid": name_random(8, "reversshiq"),
    # "from": ObjectXmpp().boundjid.bare,
    # "data": {
    # "ipARS": ipARS,
    # "jidARS": jidARS,
    # "jidAM": jidAM,
    # "ipAM": ipAM,
    # "remoteport": remoteport,
    # "portproxy": proxyportars,
    # "type_reverse": type_reverse,
    # "port_ssh_ars": ssh_port_machine,
    # "private_key_ars": resultatinformation["get_ars_key_id_rsa"],
    # "public_key_ars": resultatinformation["get_ars_key_id_rsa_pub"],
    # },
    # }
    logging.getLogger().debug("send iqcommand to %s : %s" % (jidAM, structreverse))
    result = ObjectXmpp().iqsendpulse(jidAM, structreverse, timeout)
    logging.getLogger().debug("result iqcommand : %s" % result)
    del structreverse["data"]["private_key_ars"]
    del structreverse["data"]["public_key_ars"]
    structreverse["data"]["uninterrupted"] = uninterrupted
    return structreverse["data"]


def get_packages_list(jid, CGIGET=""):
    filter = ""
    maxperpage = 10
    start = 0
    nb_dataset = 0
    if "filter" in CGIGET:
        filter = CGIGET["filter"]
    if "maxperpage" in CGIGET:
        maxperpage = int(CGIGET["maxperpage"])
    if "start" in CGIGET:
        start = int(CGIGET["start"])
    end = start + maxperpage

    timeout = 15
    result = ObjectXmpp().iqsendpulse(
        jid, {"action": "packageslist", "data": "/var/lib/pulse2/packages"}, timeout
    )

    _result = {
        "datas": {
            "files": [],
            "description": [],
            "licenses": [],
            "name": [],
            "uuid": [],
            "os": [],
            "size": [],
            "version": [],
            "methodtransfer": [],
            "metagenerator": [],
            "count_files": [],
        },
        "total": 0,
        "nb_dataset": 0,
    }

    try:
        packages = json.loads(result)
        count = 0
        _result["datas"]["total"] = len(packages["datas"])
        pp = []
        if filter != "":
            for package in packages["datas"]:
                if (
                    re.search(filter, package["description"], re.IGNORECASE)
                    or re.search(filter, package["name"], re.IGNORECASE)
                    or re.search(filter, package["version"], re.IGNORECASE)
                    or re.search(filter, package["targetos"], re.IGNORECASE)
                    or re.search(filter, package["methodtransfer"], re.IGNORECASE)
                    or re.search(filter, package["metagenerator"], re.IGNORECASE)
                ):
                    pp.append(package)
        else:
            pp = packages["datas"]
        for package in pp[start:end]:
            nb_dataset += 1
            package["files"] = [
                [str(elem) for elem in _file] for _file in package["files"]
            ]
            _result["datas"]["files"].append(package["files"])
            _result["datas"]["description"].append(package["description"])
            _result["datas"]["licenses"].append(package["licenses"])
            _result["datas"]["name"].append(package["name"])
            _result["datas"]["uuid"].append(package["uuid"].split("/")[-1])
            _result["datas"]["os"].append(package["targetos"])
            _result["datas"]["size"].append(str(package["size"]))
            _result["datas"]["version"].append(package["version"])
            _result["datas"]["methodtransfer"].append(package["methodtransfer"])
            _result["datas"]["metagenerator"].append(package["metagenerator"])
            _result["datas"]["count_files"].append(package["count_files"])
        _result["total"] = len(pp)
        _result["nb_dataset"] = nb_dataset
    except Exception as e:
        logging.error(e)
        pass

    return _result


def getPanelsForMachine(hostname):
    return manage_grafana(hostname).grafanaGetPanels()


def getPanelImage(hostname, panel_title, from_timestamp, to_timestamp):
    return manage_grafana(hostname).grafanaGetPanelImage(
        panel_title, from_timestamp, to_timestamp
    )


def getPanelGraph(hostname, panel_title, from_timestamp, to_timestamp):
    return manage_grafana(hostname).grafanaGetPanelGraph(
        panel_title, from_timestamp, to_timestamp
    )


def getLastOnlineStatus(jid):
    result = XmppMasterDatabase().last_event_presence_xmpp(jid)
    try:
        return result[0]["status"]
    except:
        return False


def get_mon_events(start, maxperpage, filter):
    result = XmppMasterDatabase().get_mon_events(start, maxperpage, filter)
    return result


def get_mon_events_history(start, maxperpage, filter):
    result = XmppMasterDatabase().get_mon_events_history(start, maxperpage, filter)
    return result


def acquit_mon_event(id, user):
    result = XmppMasterDatabase().acquit_mon_event(id, user)
    return result


def dir_exists(path):
    return os.path.isdir(path)


def create_dir(path):
    try:
        os.makedirs(path, 0o755)
        return True
    except OSError:
        return False


def file_exists(path):
    return os.path.isfile(path)


def create_file(path):
    with open(path, "a") as new_file:
        new_file.write("")
        new_file.close()


def get_content(path):
    content = ""
    if path != "" and file_exists(path):
        with open(path, "r") as file:
            content = file.read()
            file.close()
    return content


def write_content(path, datas, mode="w"):
    content = ""
    if mode not in ["a", "w"]:
        mode = "w"

    olddatas = get_content(path)

    md5sum_old = hashlib.md5(olddatas).hexdigest()
    md5sum_new = hashlib.md5(datas).hexdigest()

    if path != "" and file_exists(path):
        try:
            with open(path, mode) as file:
                if md5sum_old != md5sum_new:
                    content = file.write(datas)
                file.close()
                return True
        except:
            return False


def get_computer_count_for_dashboard():
    return xmlrpcCleanup(XmppMasterDatabase().get_computer_count_for_dashboard())


def get_count_success_rate_for_dashboard():
    result = XmppMasterDatabase().get_count_success_rate_for_dashboard()
    return result


def get_count_total_deploy_for_dashboard():
    result = XmppMasterDatabase().get_count_total_deploy_for_dashboard()
    return result


def get_ars_from_cluster(id, filter=""):
    result = XmppMasterDatabase().get_ars_from_cluster(id, filter)
    return result


def update_cluster(id, name, description, relay_ids):
    result = XmppMasterDatabase().update_cluster(id, name, description, relay_ids)
    return result


def create_cluster(name, description, relay_ids):
    result = XmppMasterDatabase().create_cluster(name, description, relay_ids)
    return result


def get_rules_list(start, end, filter):
    return XmppMasterDatabase().get_rules_list(start, end, filter)


def order_relay_rule(action, id):
    result = XmppMasterDatabase().order_relay_rule(action, id)
    return result


def get_relay_rules(id, start, end, filter):
    return XmppMasterDatabase().get_relay_rules(id, start, end, filter)


def new_rule_order_relay(id):
    return XmppMasterDatabase().new_rule_order_relay(id)


def add_rule_to_relay(relay_id, rule_id, order, subject):
    return XmppMasterDatabase().add_rule_to_relay(relay_id, rule_id, order, subject)


def delete_rule_relay(rule_id):
    return XmppMasterDatabase().delete_rule_relay(rule_id)


def move_relay_rule(relay_id, rule_id, action):
    return XmppMasterDatabase().move_relay_rule(relay_id, rule_id, action)


def get_relay_rule(rule_id):
    return XmppMasterDatabase().get_relay_rule(rule_id)


def get_relays_for_rule(rule_id, start, end, filter):
    return XmppMasterDatabase().get_relays_for_rule(rule_id, start, end, filter)


def edit_rule_to_relay(id, relay_id, rule_id, subject):
    return XmppMasterDatabase().edit_rule_to_relay(id, relay_id, rule_id, subject)


def get_minimal_relays_list(mode):
    return XmppMasterDatabase().get_minimal_relays_list(mode)


def get_count_agent_for_dashboard():
    result = XmppMasterDatabase().get_count_agent_for_dashboard()
    return result


def get_machines_for_ban(jid_ars, start=0, end=-1, filter=""):
    result = XmppMasterDatabase().get_machines_for_ban(jid_ars, start, end, filter)
    return result


def get_machines_to_unban(jid_ars, start=0, end=-1, filter=""):
    result = XmppMasterDatabase().get_machines_to_unban(jid_ars, start, end, filter)
    return result


def get_conformity_update_by_machine(idmachine):
    result = XmppMasterDatabase().get_conformity_update_by_machine(idmachine)
    return result


def get_conformity_update_for_group(uuidArray):
    result = XmppMasterDatabase().get_conformity_update_for_group(uuidArray)
    nbmachinetotal = len(uuidArray)
    result[0]["pending_updates"] = int(result[0]["pending_updates"])

    if result[0]["count_machines"] == 0 or result[0]["pending_updates"] == 0:
        result[0]["compliance"] = 100
    else:
        result[0]["compliance"] = (
            (float(nbmachinetotal) - float(result[0]["count_machines"]))
            / float(nbmachinetotal)
            * 100.0
        )
    return result


def get_idmachine_from_name(name):
    result = XmppMasterDatabase().get_idmachine_from_name(name)
    return result


def get_count_updates_enable():
    result = XmppMasterDatabase().get_count_updates_enable()
    return result


def ban_machines(subaction, jid_ars, machines):
    sessionid = name_random(8, "banmachines")
    boundjidbare = "master@pulse/MASTER"
    # datasend = {
    # "action": "banmachines",
    # "from": ObjectXmpp().boundjid.bare,
    # "sessionid": sessionid,
    # "data": {"subaction": subaction, "jid_ars": jid_ars, "jid_machines": machines},
    # "base64": False,
    # }
    datasend = {
        "action": "banmachines",
        "from": boundjidbare,
        "sessionid": sessionid,
        "data": {"subaction": subaction, "jid_ars": jid_ars, "jid_machines": machines},
        "base64": False,
    }
    callXmppPlugin("banmachines", datasend)

    return True


def reload_deploy(
    uuid,
    cmd_id,
    gid,
    sessionid,
    hostname,
    login,
    title,
    start,
    endcmd,
    startcmd,
    force_redeploy,
    rechedule,
):
    result = XmppMasterDatabase().reload_deploy(
        uuid,
        cmd_id,
        gid,
        sessionid,
        hostname,
        login,
        title,
        start,
        endcmd,
        startcmd,
        force_redeploy,
        rechedule,
    )


def get_updates_by_entity(entity, start=0, limit=-1, filter=""):
    return XmppMasterDatabase().get_updates_by_entity(entity, start, limit, filter)


def get_updates_machines_by_entity(entity, pid, start=0, limit=-1, filter=""):
    return XmppMasterDatabase().get_updates_machines_by_entity(
        entity, pid, start, limit, filter
    )


def pending_entity_update_by_pid(entity, pid, startdate="", enddate="", interval=""):
    return XmppMasterDatabase().pending_entity_update_by_pid(
        entity, pid, startdate, enddate, interval
    )


def pending_group_update_by_pid(gid, pid, startdate="", enddate=""):
    pass


def pending_machine_update_by_pid(
    machineid,
    inventoryid,
    updateid,
    deployName,
    user,
    startdate="",
    enddate="",
    interval="",
):
    return XmppMasterDatabase().pending_machine_update_by_pid(
        machineid, inventoryid, updateid, deployName, user, startdate, enddate, interval
    )


def get_updates_by_uuids(uuids, start=0, limit=-1, filter=""):
    return XmppMasterDatabase().get_updates_by_uuids(uuids, start, limit, filter)


def get_updates_by_machineids(machineids, start=0, limit=-1, filter=""):
    return XmppMasterDatabase().get_updates_by_machineids(
        machineids, start, limit, filter
    )


def get_tagged_updates_by_machine(machineid, start=0, end=-1, filter=""):
    return XmppMasterDatabase().get_tagged_updates_by_machine(
        machineid, start, end, filter
    )


def get_audit_summary_updates_by_machine(machineid, start=0, end=-1, filter=""):
    return XmppMasterDatabase().get_audit_summary_updates_by_machine(
        machineid, start, end, filter
    )


def get_update_kb(updateid):
    return XmppMasterDatabase().get_update_kb(updateid)


def cancel_update(machineid, updateid):
    return XmppMasterDatabase().cancel_update(machineid, updateid)
