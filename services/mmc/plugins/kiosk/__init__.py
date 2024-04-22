# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Plugin to manage the interface with Kiosk
"""
import logging
import uuid
import os
import base64
import re

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.support.config import PluginConfigFactory
from mmc.plugins.kiosk.config import KioskConfig
from mmc.plugins.kiosk.TreeOU import TreeOU
from mmc.plugins.base.config import BasePluginConfig
from mmc.plugins.xmppmaster.master.lib.utils import name_random


# Database
from pulse2.database.kiosk import KioskDatabase
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
from distutils.version import LooseVersion, StrictVersion

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
    config = KioskConfig("kiosk")

    # Registering KioskComputers in ComputerManager
    # ComputerManager().register('kiosk', KioskComputers)

    if config.disable:
        logger.warning("Plugin kiosk: disabled by configuration.")
        return False

    if not KioskDatabase().activate(config):
        logger.warning(
            "Plugin kiosk: an error occurred during the database initialization"
        )
        return False
    return True


# #############################################################
# KIOSK DATABASE FUNCTIONS
# #############################################################


def get_profiles_list(login, start=0, limit=-1, filter=""):
    teammates = XmppMasterDatabase().get_teammembers_from_login(login)
    if login == "root":
        return KioskDatabase().get_profiles_list(start, limit, filter)
    else:
        if teammates == []:
            teammates.append(login)
        return KioskDatabase().get_profiles_list_team(teammates, start, limit, filter)


def get_profiles_name_list():
    return KioskDatabase().get_profiles_name_list()


def create_profile(name, login, ous, active, packages, source):
    result = KioskDatabase().create_profile(name, login, ous, active, packages, source)
    notify_kiosks()
    return result


def delete_profile(id):
    result = KioskDatabase().delete_profile(id)
    notify_kiosks()
    return result


def get_profile_by_id(id):
    return KioskDatabase().get_profile_by_id(id)


def update_profile(login, id, name, ous, active, packages, source):
    result = KioskDatabase().update_profile(
        login, id, name, ous, active, packages, source
    )
    notify_kiosks()
    return result


# #############################################################
# KIOSK GENERAL FUNCTIONS
# #############################################################
def get_ou_list(source, *args, **kwargs):
    """This function returns the list of OUs

    Returns:
        list of strings. The strings are the OUs
        or
        returns False for some issues
    """
    funcname = "get_ou_list_%s" % (source.lower())
    try:
        func = globals()[funcname]
        # Step 1 - Get datas
        datas = func(*args, **kwargs)
        # Step 2 - Recreate OUs tree
        tree = TreeOU()
        for line in datas:
            tree.create_recursively(line)

        return tree.recursive_json()
    except:
        return []


def get_ou_list_ou_machine(*args, **kwargs):
    ous = XmppMasterDatabase().get_oumachine_list_from_machines()
    return ous


def get_ou_list_ou_user(*args, **kwargs):
    ous = XmppMasterDatabase().get_ouuser_list_from_machines()
    return ous


def get_ou_list_ldap(*args, **kwargs):
    # Check the ldap config
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    kconfig = KioskConfig("kiosk")

    ous = []
    if config.has_section("authentication_externalldap"):
        id = str(uuid.uuid4())
        file = "/tmp/ous-" + id

        # Get the parameters from the config file
        ldapurl = config.get("authentication_externalldap", "ldapurl")
        suffix = config.get("authentication_externalldap", "suffix_ou")
        bindname = config.get("authentication_externalldap", "bindname")
        bindpasswd = config.get("authentication_externalldap", "bindpasswd")

        # Execute the command which get the OU list and write into the specified file
        command = """ldapsearch -o ldif-wrap=no -H %s -x -b "%s" -D "%s" -w %s -LLL "(
        objectClass=organizationalUnit)" dn > %s""" % (
            ldapurl,
            suffix,
            bindname,
            bindpasswd,
            file,
        )

        os.system(command)

        ous = []
        # Parse the file
        with open(file, "r") as ou_file:
            lines = ou_file.read().splitlines()
            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith("dn")]

            # Parse the result for each lines
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith("dn:: "):
                    tmp = element.split("::")
                    ou = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(": ")
                    ou = tmp[1]
                # Format the result
                ou = ou.replace(",OU=", " < ")
                ou = ou.replace("OU=", "")
                ou = re.sub(",DC=(.+)", "", ou)

                ou = ou.split(" < ")
                ou.reverse()
                ou = "/".join(ou)
                # Save the content into a list
                ous.append(ou)

        # Delete the file
        os.remove(file)
    else:
        return False


def get_ou_list_group(login, *args, **kwargs):
    teammates = XmppMasterDatabase().get_teammembers_from_login(login)
    if login == "root":
        return XmppMasterDatabase().get_all_ad_groups()
    else:
        if teammates == []:
            teammates.append(login)
        return XmppMasterDatabase().get_all_ad_groups_team(teammates)


def get_ou_list_entity(*args, **kwargs):
    ous = []
    ous = XmppMasterDatabase().get_ou_list_from_entity()
    return ous


def get_ou_tree():
    """This function returns the list of OUs

    Returns:
        TreeOU object which contains all the OUs.
        or
        returns False for some issues
    """

    # Check the ldap config
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    kconfig = KioskConfig("kiosk")

    ous = []

    if kconfig.use_external_ldap is False:
        ous = XmppMasterDatabase().get_ou_list_from_machines()
    elif config.has_section("authentication_externalldap"):
        id = str(uuid.uuid4())
        file = "/tmp/ous-" + id

        # Get the parameters from the config file
        ldapurl = config.get("authentication_externalldap", "ldapurl")
        suffix = config.get("authentication_externalldap", "suffix_ou")
        bindname = config.get("authentication_externalldap", "bindname")
        bindpasswd = config.get("authentication_externalldap", "bindpasswd")

        # Execute the command which get the OU list and write into the specified file
        command = """ldapsearch -o ldif-wrap=no -H %s -x -b "%s" -D "%s" -w %s -LLL "(
        objectClass=organizationalUnit)" dn > %s""" % (
            ldapurl,
            suffix,
            bindname,
            bindpasswd,
            file,
        )

        os.system(command)

        # Parse the file
        with open(file, "r") as ou_file:
            lines = ou_file.read().splitlines()
            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith("dn")]

            # Parse the result for each lines
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith("dn:: "):
                    tmp = element.split("::")
                    ou = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(": ")
                    ou = tmp[1]
                # Format the result
                ou = ou.replace(",OU=", " < ")
                ou = ou.replace("OU=", "")
                ou = re.sub(",DC=(.+)", "", ou)

                ou = ou.split(" < ")
                ou.reverse()
                ou = "/".join(ou)
                # Save the content into a list
                ous.append(ou)

        # Delete the file
        os.remove(file)
    else:
        return False
    return ous


def str_to_ou(string):
    return TreeOU().str_to_ou(string)


def get_users_from_ou(ou):
    """This function returns the list of user for the specified ou.

    Params:
        string OU must be formatted like path : /root/son/grand_son. See TreeOU.get_path() method to obtain this
        kind of string from the initial OU string.

    Returns:
        list of strings. The strings are the OUs
        or
        returns False for some issues
    """
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    kconfig = KioskConfig("kiosk")

    users = []
    if kconfig.use_external_ldap is False:
        # ou = ou.replace("/", "@@")
        users = XmppMasterDatabase().get_users_from_ou_from_machines(ou)
    elif config.has_section("authentication_externalldap"):
        ou = str_to_ou(ou)

        id = str(uuid.uuid4())
        file = "/tmp/users_ou-" + id

        # Get the parameters from the config file
        ldapurl = config.get("authentication_externalldap", "ldapurl")
        bindname = config.get("authentication_externalldap", "bindname")
        bindpasswd = config.get("authentication_externalldap", "bindpasswd")

        command = """ldapsearch -o ldif-wrap=no -H %s -x -b "%s" -D "%s" -w %s -LLL "(&(!(objectclass=computer))
        (objectclass=person))" dn > %s""" % (
            ldapurl,
            ou,
            bindname,
            bindpasswd,
            file,
        )

        os.system(command)
        # Parse the file
        with open(file, "r") as user_file:
            lines = user_file.read().splitlines()

            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith("dn")]
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith("dn:: "):
                    tmp = element.split("::")
                    cn = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(": ")
                    cn = tmp[1]
                # Format the result
                cn = re.sub("CN=", "", cn)
                cn = re.sub(",OU=(.+)", "", cn)

                # Save the content into a list
                users.append(cn)

        # Delete the file
        os.remove(file)
    else:
        return False
    return users


def handlerkioskpresence(
    jid, id, os, hostname, uuid_inventorymachine, agenttype, classutil, fromplugin=False
):
    """
    This function launch the kiosk actions when a prensence machine is active
    """
    logger.debug("kiosk handled")
    # print jid, id, os, hostname, uuid_inventorymachine, agenttype, classutil
    # get the profiles from the table machine.
    machine = XmppMasterDatabase().getMachinefromjid(jid)
    structuredatakiosk = get_packages_for_machine(machine)
    datas = {
        "subaction": "initialisation_kiosk",
        "data": {"action": "packages", "packages_list": structuredatakiosk},
    }

    if not fromplugin:
        send_message_to_machine(datas, jid, name_random(6, "initialisation_kiosk"))
    return datas


def __search_software_in_glpi(
    list_software_glpi, list_granted_packages, packageprofile, structuredatakiosk
):
    structuredatakioskelement = {
        "name": packageprofile[0],
        "action": [],
        "uuid": packageprofile[6],
        "description": packageprofile[2],
        "version": packageprofile[3],
        "profile": packageprofile[1],
    }
    patternname = re.compile(
        "(?i)"
        + packageprofile[4]
        .replace("+", "\+")
        .replace("*", "\*")
        .replace("(", "\(")
        .replace(")", "\)")
        .replace(".", "\.")
    )
    for soft_glpi in list_software_glpi:
        if (
            patternname.match(str(soft_glpi[0]))
            or patternname.match(str(soft_glpi[1]))
            or (soft_glpi[1] == packageprofile[4] and soft_glpi[2] == packageprofile[5])
        ):
            # Process with this package which is installed on the machine
            # The package could be deleted
            structuredatakioskelement["icon"] = "kiosk.png"
            structuredatakioskelement["action"].append("Delete")
            structuredatakioskelement["action"].append("Launch")
            # verification if update
            # compare the version
            # TODO
            # For now we use the package version. Later the software version will be needed into the pulse package
            if LooseVersion(soft_glpi[2]) < LooseVersion(packageprofile[3]):
                structuredatakioskelement["action"].append("Update")
                logger.debug(
                    "the software version is superior "
                    "to that installed on the machine %s : %s < %s"
                    % (packageprofile[0], soft_glpi[2], LooseVersion(packageprofile[3]))
                )
            break
    if len(structuredatakioskelement["action"]) == 0:
        # The package defined for this profile is absent from the machine:
        if packageprofile[8] == "allowed":
            structuredatakioskelement["action"].append("Install")
        else:
            trigger = False
            for ack in list_granted_packages:
                if ack["package_uuid"] == structuredatakioskelement["uuid"]:
                    if ack["id_package_has_profil"] != packageprofile[9]:
                        continue
                    else:
                        if ack["status"] == "allowed":
                            structuredatakioskelement["action"].append("Install")
                        elif ack["status"] == "waiting":
                            trigger = True
                        elif ack["status"] == "rejected":
                            trigger = True
                else:
                    continue

            if len(structuredatakioskelement["action"]) == 0 and trigger is False:
                structuredatakioskelement["action"].append("Ask")

    return structuredatakioskelement


def send_message_to_machine(
    datas, jid, sessionid=None, subaction="send_message_to_jid"
):
    from mmc.plugins.xmppmaster.master.agentmaster import callXmppPlugin

    # use plugin master kiosk for send msg
    datasend = {"subaction": subaction, "jid": jid, "data": datas}

    if sessionid is not None:
        datasend["sessionid"] = name_random(6, "sendmsgmachine")

    else:
        datasend["sessionid"] = sessionid
    callXmppPlugin("kiosk", datasend)


def test_call_xmpp_plugin_master(jid):
    datas = {"subaction": "test"}

    send_message_to_machine(datas, jid)


def get_ou_for_user(user):
    """This function find the ou of the specified user.

    Params:
        string user name

    Returns:
        The string of the OU
        or
        returns False for some issues
    """
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    kconfig = KioskConfig("kiosk")

    ous = []
    if kconfig.use_external_ldap is False:
        ous = XmppMasterDatabase().get_ou_for_user_from_machines(user)
    elif config.has_section("authentication_externalldap"):
        id = str(uuid.uuid4())
        file = "/tmp/ou_user-" + id

        # Get the parameters from the config file
        ldapurl = config.get("authentication_externalldap", "ldapurl")
        suffix = config.get("authentication_externalldap", "suffix_ou")
        bindname = config.get("authentication_externalldap", "bindname")
        bindpasswd = config.get("authentication_externalldap", "bindpasswd")

        command = """ldapsearch -o ldif-wrap=no -H "%s" -x -b "%s" -D "%s" -w %s -LLL "(&(objectclass=user)
        (samaccountname=%s))" dn > %s""" % (
            ldapurl,
            suffix,
            bindname,
            bindpasswd,
            user,
            file,
        )

        os.system(command)
        with open(file, "r") as user_file:
            lines = user_file.read().splitlines()

            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith("dn")]
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith("dn:: "):
                    tmp = element.split("::")
                    ou = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(": ")
                    ou = tmp[1]
                # Format the result
                # Format the result
                ou = re.sub("CN=" + user + ",", "", ou)
                ou = re.sub(",DC=(.+)", "", ou)
                ou = ou.replace(",OU=", " < ")
                ou = ou.replace("OU=", "")

                ou = ou.split(" < ")
                ou.reverse()
                ou = "/".join(ou)
                # Save the content into a list
                ous.append(ou)
        # Delete the file
        os.remove(file)
    else:
        return False
    return ous


def notify_kiosks():
    """This function send a notification message for all the machine which have a kiosk on it."""

    machines_list = XmppMasterDatabase().get_machines_with_kiosk()

    for machine in machines_list:
        structuredatakiosk = get_packages_for_machine(machine)
        datas = {
            "subaction": "profiles_updated",
            "data": {"action": "packages", "packages_list": structuredatakiosk},
        }
        send_message_to_machine(
            datas, machine["jid"], name_random(6, "profiles_updated")
        )


def notify_kiosk(machine):
    """This function send a notification message for the specified machine.
    Param:
        machine : XmppMasterDatabase.Machine object
    """

    structuredatakiosk = get_packages_for_machine(machine)
    datas = {
        "subaction": "profiles_updated",
        "data": {"action": "packages", "packages_list": structuredatakiosk},
    }
    send_message_to_machine(datas, machine["jid"], name_random(6, "profiles_updated"))


def get_packages_for_machine(machine):
    """Get a list of the packages for the concerned machine.
    Param:
        machine : dict of the machine datas.
        Data structure:
        { "ad_ou_machine":"somethine", "ad_ou_user": "something", "hostname":"machine-name", "uuid_inventorymachine":"UUID1"}
    Returns:
        list of the packages"""

    machine_entity = XmppMasterDatabase().getmachineentityfromjid(machine["jid"])
    machine_entity = (
        machine_entity.complete_name.replace(" > ", "/")
        if machine_entity is not None
        else None
    )
    OUmachine = (
        machine["ad_ou_machine"].replace("\n", "").replace("\r", "").replace("@@", "/")
    )
    OUuser = (
        machine["ad_ou_user"].replace("\n", "").replace("\r", "").replace("@@", "/")
    )
    group = XmppMasterDatabase().get_ad_group_for_lastuser(machine["lastuser"])
    if OUmachine == "":
        OUmachine = None
    if OUuser == "":
        OUuser == None

    ldap = get_ou_for_user(machine["lastuser"])
    ldap = None if ldap is False else ldap

    _sources = {
        "ou_machine": OUmachine,
        "ou_user": OUuser,
        "ldap": ldap,
        "group": group,
        "entity": machine_entity,
    }
    # remove empty values and delete the temp _sources variable
    sources = {key: _sources[key] for key in _sources if _sources[key] != None}

    # we find all profiles with the specified sources
    profiles = KioskDatabase().get_profiles_by_sources(sources)

    # search packages for the applied profiles
    list_profile_packages = KioskDatabase().get_profile_list_for_profiles_list(profiles)
    if list_profile_packages is None:
        return []

    granted_packages = []
    for element in list_profile_packages:
        granted_packages += KioskDatabase().get_acknowledges_for_package_profile(
            element[9], element[6], machine["lastuser"]
        )
    list_software_glpi = []
    softwareonmachine = Glpi().getLastMachineInventoryPart(
        machine["uuid_inventorymachine"],
        "Softwares",
        0,
        -1,
        "",
        {"hide_win_updates": True, "history_delta": ""},
    )
    for x in softwareonmachine:
        list_software_glpi.append([x[0][1], x[1][1], x[2][1]])

    structuredatakiosk = []

    indexed = {}
    # Create structuredatakiosk for initialization
    for packageprofile in list_profile_packages:
        spkg = __search_software_in_glpi(list_software_glpi, granted_packages, packageprofile)

        if spkg['name'] not in indexed:
            structuredatakiosk.append(spkg)
            indexed[spkg['name']] = {
                "action": spkg['action'],
                "id": len(structuredatakiosk)-1
            }
        else:
            #ask < install < delete
            # check if indexed has more rights than spkg
            if "Delete" in indexed[spkg['name']]["action"] and "Delete" not in spkg["action"]:
                # spkg["name"]][id] = id of spkg in structuredatakiosk
                #change the action of the package stored in structuredatakiosk
                structuredatakiosk[indexed[spkg["name"]][id]]["action"] = ["Delete"]
                if "Launch" in indexed[spkg["name"]]["action"]:
                    structuredatakiosk[indexed[spkg["name"]][id]]["action"].append("Launch")

            elif "Install" in indexed[spkg["name"]] and "Ask" in indexed[spkg["action"]]:
                continue
    logger.debug(
        "initialisation kiosk %s on machine %s"
        % (structuredatakiosk, machine["hostname"])
    )

    return structuredatakiosk


def update_launcher(uuid, launcher):
    """Send the new launcher for the specified package.
    Params:
        uuid: str which contains the uuid of the package.
        launcher: str or base64 str of the launcher

    Emits:
        "update_launcher" subaction for kiosk_plugin
    """

    datas = {
        "subaction": "update_launcher",
        "data": {"uuid": uuid, "launcher": launcher},
    }

    machines_list = XmppMasterDatabase().get_machines_with_kiosk()
    for machine in machines_list:
        # Send the launcher to all the machines
        send_message_to_machine(
            datas, machine["jid"], name_random(6, "update_launcher")
        )

        # Update the datas for all the kiosks
        structuredatakiosk = get_packages_for_machine(machine)
    notify_kiosks()


def get_acknowledges_for_sharings(sharings, start=0, limit=-1, filter=""):
    acknowledges = KioskDatabase().get_acknowledges_for_sharings(
        sharings, start, limit, filter
    )

    return acknowledges


def update_acknowledgement(id, acknowledgedbyuser, startdate, enddate, status):
    result = KioskDatabase().update_acknowledgement(
        id, acknowledgedbyuser, startdate, enddate, status
    )

    return result


def get_conf_kiosk():
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    kconfig = KioskConfig("kiosk")

    result = {
        "use_external_ldap": kconfig.use_external_ldap,
        "enable_acknowledgements": kconfig.enable_acknowledgements,
    }

    return result
