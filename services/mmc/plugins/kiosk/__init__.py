# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Plugin to manage the interface with Kiosk
"""
import logging
import uuid
import os
import base64
import re
import json

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.support.config import PluginConfigFactory
from mmc.plugins.kiosk.config import KioskConfig
from mmc.plugins.kiosk.TreeOU import TreeOU
from mmc.plugins.base.config import BasePluginConfig
from mmc.plugins.xmppmaster.master.lib.utils import name_random


from mmc.support.mmctools import (
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_xmpp_context,
                              with_optional_xmpp_context,)
# Database
from pulse2.database.kiosk import KioskDatabase
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.admin import get_list_user_token, get_entities_with_counts_root
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
        logger.error(
            "Plugin kiosk: an error occurred during the database initialization"
        )
        return False
    return True


class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s



class RpcProxy(RpcProxyI):

    @with_optional_xmpp_context
    def create_profile(self,
                       name,
                       login,
                       ous,
                       active,
                       packages,
                       source,
                       ctx=None):
        result = KioskDatabase().create_profile(name, login, ous, active, packages, source)
        notify_kiosks()
        return result
# #############################################################
# KIOSK DATABASE FUNCTIONS
# #############################################################

    @with_optional_xmpp_context
    def get_profiles_list(self, login, start=0, limit=-1, filter="", ctx=None):
        if login == "root":
            return KioskDatabase().get_profiles_list(start, limit, filter)
        else:
            patterns = XmppMasterDatabase().get_team_patterns_from_login(login)
            if patterns == []:
                patterns = [login]
            result = KioskDatabase().get_profiles_list_team(patterns, start, limit, filter)
            return result

    @with_optional_xmpp_context
    def get_profiles_name_list(self, ctx=None):
        return KioskDatabase().get_profiles_name_list()

    @with_optional_xmpp_context
    def delete_profile(self, id, ctx=None):
        result = KioskDatabase().delete_profile(id)
        notify_kiosks()
        return result

    @with_optional_xmpp_context
    def get_profile_by_id(self, id, ctx=None):
        return KioskDatabase().get_profile_by_id(id)

    @with_optional_xmpp_context
    def update_profile(self, login, id, name, ous, active, packages, source, ctx=None):
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
                ou = ">>".join(ou)
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
    """
    Returns the list of GLPI entities the user has access to
    """
    token = args[1]
    allowed_glpi_ids = {int(x) for x in (get_list_user_token(token) or [])}
    logger.debug(f"IDs GLPI autorisés : {allowed_glpi_ids}")

    rule_entity = get_entities_with_counts_root('', 0, 1, list(allowed_glpi_ids))
    data = (rule_entity or {}).get('data', {})
    ids = data.get('id', []) or []
    completes = data.get('completename', []) or []
    logger.debug(f"IDs des entités GLPI : {ids}")
    logger.debug(f"Completenames des entités GLPI : {completes}")

    # Build the list of all authorized entity paths
    result = []
    for i, c in zip(ids, completes):
        try:
            gid = int(i)
        except Exception:
            continue
        if gid in allowed_glpi_ids:
            result.append(str(c))

    logger.debug(f"Entités GLPI retournées : {result}")
    return result


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
                ou = ">>".join(ou)
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
                ou = ">>".join(ou)
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
        if machine["uuid_inventorymachine"] == "":
            continue
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

    # We have to check the packages OS from profiles list, and verify if they are compatible with the current machine


    # Get the machine OS
    platform = "win"
    mach_platform = ""
    if "platform" in machine:
        # Because re is picky, we have to use an independant str
        mach_platform = machine["platform"]
        if re.match("Microsoft", mach_platform) is not None:
            platform = "win"
        elif re.match("Darwin", mach_platform) is not None or re.match("MacOS", mach_platform) is not None:
            platform = "mac"
        else:
            platform = "linux"

    #
    # Setting up the sources datas info
    #
    machine_entity = XmppMasterDatabase().getmachineentityfromjid(machine["jid"])
    machine_entity = (
        machine_entity.complete_name.replace(" > ", ">>")
        if machine_entity is not None
        else None
    )
    OUmachine = (
        machine["ad_ou_machine"].replace("\n", "").replace("\r", "").replace("@@", ">>")
    )
    OUuser = (
        machine["ad_ou_user"].replace("\n", "").replace("\r", "").replace("@@", ">>")
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

    # search packages and acknowledgements for the applied profiles
    list_profile_packages = KioskDatabase().get_packages_for_profile_list(profiles)
    if list_profile_packages is None or list_profile_packages == []:
        return []
    # Define the path for the packages list. Needed to find some info from xmppdeploy.json
    pkg_dir = os.path.join("/", "var","lib", "pulse2", "packages")


    # pkg_statuses is the cleaned up list of packages associated to the profiles list.
    #   We will determine some info from packages and machine:
    #       such OS compatibility between package and machine,
    #       if the uninstall section is pecified,
    #       if the launcher command is specified ...
    #       the rights allowed, acknowledged, rejected ....

    pkg_statuses = {}
    for pkg in list_profile_packages:
        # get a shortcut to package uuid
        uuid = pkg["package_uuid"]

        ### Check if the packages found are OS compatible
        depl = {}
        pkg_path = os.path.join(pkg_dir, uuid, "xmppdeploy.json")
        try:
            with open(pkg_path, "r") as fb:
                try:
                    depl = json.load(fb)
                except:
                    depl = {}
                finally:
                    fb.close()
        except:
            # Can't read xmppdeploy.json : probably corrupted package : skip
            continue

        # Check if the machine OS is compatible with the package
        if platform not in pkg["os"]:
            continue

        # Check if the uninstall section is present
        uninstall_section_present = False
        update_section_present = False
        for action_name in depl["metaparameter"][platform]["label"]:
            if action_name == action_name.startswith("upd_"):
                uninstall_section_present = True
            if action_name == "label_section_uninstall" or action_name.startswith("Uninst_"):
                uninstall_section_present = True

        # Check if the launcher is specified
        launcher = ""
        if depl["info"]["launcher"] != "":
            launcher = depl["info"]["launcher"]

        # Check if the package is installed on the machine
        found = Glpi().find_software_info_for_machine(machine["uuid_inventorymachine"],  pkg)
        installed = True if found != [] else False
        # create a new entry for this package if not existing in pkg_statuses
        if uuid not in pkg_statuses:
            # By default set to restricted
            pkg_statuses[uuid] = {
                "icon": "kiosk.png",
                "right": "restricted",
                "launcher" : launcher,
                "uninstall" : uninstall_section_present,
                "update": update_section_present,
                "installed" : installed,
                "uuid" : uuid,
                "version_software": pkg["version_software"],
                "vendor": pkg["vendor"],
                "version": pkg["version_package"],
                "software": pkg["software"],
                "description": pkg["description"],
                "name":pkg["name_package"],
                "action": []
            }

        # We will find some info from profile rights
        if pkg["package_status"] == "allowed":
            pkg_statuses[uuid]["right"] = "allowed"

        elif pkg["package_status"] == "restricted" and pkg["status"] == "allowed":
            pkg_statuses[uuid]["right"] = "allowed"

        # We fully know the package rights and states: we can put actions on it
        pkg_statuses[uuid]["action"] = []

        if installed == False:
            if pkg_statuses[uuid]["right"] == "allowed":
                pkg_statuses[uuid]["action"].append("Install")
            else:
                pkg_statuses[uuid]["action"].append("Ask")
        else:
            if pkg_statuses[uuid]["launcher"] != "":
                pkg_statuses[uuid]["action"].append("Launch")
            if pkg_statuses[uuid]["uninstall"] is True:
                pkg_statuses[uuid]["action"].append("Delete")
            if pkg_statuses[uuid]["update"] is True:
                if LooseVersion(found[0][2]) < LooseVersion(pkg["version"]):
                    pkg_statuses[uuid]["action"].append("Update")

    structuredatakiosk = []
    for uuid in pkg_statuses:
        structuredatakiosk.append(pkg_statuses[uuid])

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
