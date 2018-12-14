# -*- coding: utf-8; -*-
#
# (c) 2018 siveo, http://www.siveo.net
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

# File : mmc/plugins/kiosk/__init__.py

"""
Plugin to manage the interface with Kiosk
"""
import logging
import json
import uuid
import os
import base64
import re

from pulse2.version import getVersion, getRevision # pyflakes.ignore

from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.kiosk.config import KioskConfig
from mmc.plugins.kiosk.TreeOU import TreeOU
from mmc.plugins.base import ComputerI
from mmc.plugins.base.config import BasePluginConfig
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.xmppmaster.master.lib.utils import name_random



# Database
from pulse2.database.kiosk import KioskDatabase
#use database xmppmaster
from pulse2.database.xmppmaster import XmppMasterDatabase
#use database glpi
from mmc.plugins.glpi.database import Glpi
#lib coparaison de version
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
        logger.warning("Plugin kiosk: an error occurred during the database initialization")
        return False
    return True


# #############################################################
# KIOSK DATABASE FUNCTIONS
# #############################################################

def get_profiles_list():
    return KioskDatabase().get_profiles_list()


def get_profiles_name_list():
    return KioskDatabase().get_profiles_name_list()


def create_profile(name, ous, active, packages):
    result = KioskDatabase().create_profile(name, ous, active, packages)
    notify_kiosks()
    return result

def delete_profile(id):
    result = KioskDatabase().delete_profile(id)
    notify_kiosks()
    return result


def get_profile_by_id(id):
    return KioskDatabase().get_profile_by_id(id)


def update_profile(id, name, ous, active, packages):
    result = KioskDatabase().update_profile(id, name, ous, active, packages)
    notify_kiosks()
    return result


# #############################################################
# KIOSK GENERAL FUNCTIONS
# #############################################################

def get_ou_list():
    """This function returns the list of OUs

    Returns:
        list of strings. The strings are the OUs
        or
        returns False for some issues
    """

    # Check the ldap config
    config = PluginConfigFactory.new(BasePluginConfig, "base")

    if config.has_section('authentication_externalldap'):
        id = str(uuid.uuid4())
        file = '/tmp/ous-'+id

        # Get the parameters from the config file
        ldapurl = config.get('authentication_externalldap', 'ldapurl')
        suffix = config.get('authentication_externalldap', 'suffix')
        bindname = config.get('authentication_externalldap', 'bindname')
        bindpasswd = config.get('authentication_externalldap', 'bindpasswd')

        # Execute the command which get the OU list and write into the specified file
        command = """ldapsearch -o ldif-wrap=no -H %s -x -b "%s" -D "%s" -w %s -LLL "(
        objectClass=organizationalUnit)" dn > %s""" % (ldapurl, suffix, bindname, bindpasswd, file)

        os.system(command)

        ous = []
        # Parse the file
        with open(file, 'r') as ou_file:
            lines = ou_file.read().splitlines()
            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith('dn')]

            # Parse the result for each lines
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith('dn:: '):
                    tmp = element.split('::')
                    ou = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(': ')
                    ou = tmp[1]
                # Format the result
                ou = ou.replace(',OU=', ' < ')
                ou = ou.replace('OU=', '')
                ou = re.sub(',DC=(.+)', '', ou)

                ou = ou.split(' < ')
                ou.reverse()
                ou = '/'.join(ou)
                # Save the content into a list
                ous.append(ou)

        # Delete the file
        os.remove(file)

        tree = TreeOU()
        for line in ous:
            tree.create_recursively(line)

        return tree.recursive_json()
    else:
        return False


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

    ou = str_to_ou(ou)

    if config.has_section('authentication_externalldap'):
        id = str(uuid.uuid4())
        file = '/tmp/users_ou-'+id

        # Get the parameters from the config file
        ldapurl = config.get('authentication_externalldap', 'ldapurl')
        bindname = config.get('authentication_externalldap', 'bindname')
        bindpasswd = config.get('authentication_externalldap', 'bindpasswd')

        command = """ldapsearch -o ldif-wrap=no -H %s -x -b "%s" -D "%s" -w %s -LLL "(&(!(objectclass=computer))
        (objectclass=person))" dn > %s""" % (ldapurl, ou, bindname, bindpasswd, file)

        os.system(command)
        users = []
        # Parse the file
        with open(file, 'r') as user_file:
            lines = user_file.read().splitlines()

            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith('dn')]
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith('dn:: '):
                    tmp = element.split('::')
                    cn = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(': ')
                    cn = tmp[1]
                # Format the result
                cn = re.sub('CN=','',cn)
                cn = re.sub(',OU=(.+)', '', cn)

                # Save the content into a list
                users.append(cn)

        # Delete the file
        os.remove(file)

        return users

    else:
        return False

def handlerkioskpresence(jid, id, os, hostname, uuid_inventorymachine, agenttype, classutil, fromplugin = False):
    """
    This function launch the kiosk actions when a prensence machine is active
    """
    logger.debug("kiosk handled")
    #print jid, id, os, hostname, uuid_inventorymachine, agenttype, classutil
    # get the profiles from the table machine.
    machine = XmppMasterDatabase().getMachinefromjid(jid)
    structuredatakiosk = get_packages_for_machine(machine)
    datas = {
    'subaction':'initialisation_kiosk',
    'data' : structuredatakiosk
    }

    if not fromplugin:
        send_message_to_machine(datas, jid, name_random(6, "initialisation_kiosk"))
    return datas

def __search_software_in_glpi(list_software_glpi, packageprofile, structuredatakiosk):
    structuredatakioskelement={ 'name': packageprofile[0],
                                "action" : [],
                                'uuid':  packageprofile[6],
                                'description': packageprofile[2],
                                "version" : packageprofile[3]
                               }
    patternname = re.compile("(?i)" + packageprofile[0])
    for soft_glpi in list_software_glpi:
        #TODO
        # Into the pulse package provide Vendor information for the software name
        # For now we use the package name which must match with glpi name
        if patternname.match(str(soft_glpi[0])) or patternname.match(str(soft_glpi[1])):
            # Process with this package which is installed on the machine
            # The package could be deleted
            structuredatakioskelement['icon'] =  'kiosk.png'
            structuredatakioskelement['action'].append('Delete')
            structuredatakioskelement['action'].append('Launch')
            # verification if update
            # compare the version
            #TODO
            # For now we use the package version. Later the software version will be needed into the pulse package
            if LooseVersion(soft_glpi[2]) < LooseVersion(packageprofile[3]):
                structuredatakioskelement['action'].append('Update')
                logger.debug("the software version is superior "\
                    "to that installed on the machine %s : %s < %s"%(packageprofile[0],soft_glpi[2],LooseVersion(packageprofile[3])))
            break
    if len(structuredatakioskelement['action']) == 0:
        # The package defined for this profile is absent from the machine:
        if packageprofile[8] == "allowed":
            structuredatakioskelement['action'].append('Install')
        else:
            structuredatakioskelement['action'].append('Ask')
    return structuredatakioskelement


def send_message_to_machine( datas, jid, sessionid = None, subaction = 'send_message_to_jid'):
    from mmc.plugins.xmppmaster.master.agentmaster import callXmppPlugin
    # use plugin master kiosk for send msg
    datasend={'subaction': subaction,
    'jid': jid,
    'data': datas}

    if sessionid is not None:
        datasend['sessionid'] = name_random(6, "sendmsgmachine")

    else:
        datasend['sessionid'] = sessionid
    callXmppPlugin("kiosk", datasend)


def test_call_xmpp_plugin_master(jid):
    datas = {
    'subaction':'test'
    }

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
    if config.has_section('authentication_externalldap'):
        id = str(uuid.uuid4())
        file = '/tmp/ou_user-'+id

        # Get the parameters from the config file
        ldapurl = config.get('authentication_externalldap', 'ldapurl')
        suffix = config.get('authentication_externalldap', 'suffix')
        bindname = config.get('authentication_externalldap', 'bindname')
        bindpasswd = config.get('authentication_externalldap', 'bindpasswd')

        command = """ldapsearch -o ldif-wrap=no -H "%s" -x -b "%s" -D "%s" -w %s -LLL "(&(objectclass=user)
        (samaccountname=%s))" dn > %s""" % (ldapurl, suffix, bindname, bindpasswd, user, file)

        os.system(command)
        ous = []
        with open(file, 'r') as user_file:
            lines = user_file.read().splitlines()

            # The lines that don't start by 'dn' are ignored
            lines = [element for element in lines if element.startswith('dn')]
            for element in lines:
                # Lines starts with dn:: are get in base64 format
                if element.startswith('dn:: '):
                    tmp = element.split('::')
                    ou = base64.b64decode(tmp[1])

                else:
                    tmp = element.split(': ')
                    ou = tmp[1]
                # Format the result
                # Format the result
                ou = re.sub('CN='+user+',','',ou)
                ou = re.sub(',DC=(.+)', '', ou)
                ou = ou.replace(',OU=', ' < ')
                ou = ou.replace('OU=', '')

                ou = ou.split(' < ')
                ou.reverse()
                ou = '/'.join(ou)
                # Save the content into a list
                ous.append(ou)
        # Delete the file
        os.remove(file)
        return ous
    else:
        return False

def notify_kiosks():
    """This function send a notification message for all the machine which have a kiosk on it.
    """

    machines_list = XmppMasterDatabase().get_machines_with_kiosk()

    for machine in machines_list:

        structuredatakiosk = get_packages_for_machine(machine)
        datas = {
        'subaction':'profiles_updated',
        'data' : structuredatakiosk
        }
        send_message_to_machine(datas, machine['jid'], name_random(6, "profiles_updated"))


def get_packages_for_machine(machine):
    """Get a list of the packages for the concerned machine.
    Param:
        machine : tuple of the machine datas
    Returns:
        list of the packages"""
    OUmachine = [machine['ad_ou_machine'].replace("\n",'').replace("\r",'').replace('@@','/')]
    OUuser = [machine['ad_ou_user'].replace("\n", '').replace("\r", '').replace('@@','/')]

    OU = list(set(OUmachine + OUuser))

    # search packages for the applied profiles
    list_profile_packages =  KioskDatabase().get_profile_list_for_OUList(OU)
    if list_profile_packages is None:
        #TODO
        # linux and mac os does not have an Organization Unit.
        # For mac os and linux, profile association will be done on the login name.
        return
    list_software_glpi = []
    softwareonmachine = Glpi().getLastMachineInventoryPart(machine['uuid_inventorymachine'],
                                                           'Softwares', 0, -1, '',
                                                           {'hide_win_updates': True, 'history_delta': ''})
    for x in softwareonmachine:
        list_software_glpi.append([x[0][1],x[1][1], x[2][1]])
    #print list_software_glpi # ordre information [["Vendor","Name","Version"],]
    structuredatakiosk = []

    #Create structuredatakiosk for initialization
    for packageprofile in list_profile_packages:
        structuredatakiosk.append( __search_software_in_glpi(list_software_glpi,
        packageprofile, structuredatakiosk))
    #logger.debug("initialisation kiosk %s on machine %s"%(structuredatakiosk, machine['hostname']))
    logger.debug("* initialisation kiosk on machine %s"%(machine['hostname']))
    return structuredatakiosk
