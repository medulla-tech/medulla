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
from mmc.plugins.xmppmaster.master.agentmaster import callXmppPlugin
import base64

# Database
from pulse2.database.kiosk import KioskDatabase


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
    return KioskDatabase().create_profile(name, ous, active, packages)


def delete_profile(id):
    return KioskDatabase().delete_profile(id)


def get_profile_by_id(id):
    return KioskDatabase().get_profile_by_id(id)


def update_profile(id, name, ous, active, packages):
    return KioskDatabase().update_profile(id, name, ous, active, packages)


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
        string ou must be formatted like path : /root/son/grand_son. See TreeOU.get_path() method to obtain this
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


def handlerkioskpresence(gid, id, os, hostname, uuid_inventorymachine, agenttype, classutil):
    """
    This function launch the kiosk actions when a prensence machine is active
    TODO: This function will be implemented later
    """
    print("kiosk handled")


def send_message_to_machine(datas, jid, sessionid = None):
    datasend={'subaction':'send_message_to_jid',
    'jid': jid,
    'datas': datas}

    if sessionid is not None:
        datasend['sessionid'] = namerandom(6, sendmsgmachine)

    else:
        datasend['sessionid'] = sessionid
    callXmppPlugin("kiosk", datasend)


def test_call_xmpp_plugin_master(jid):
    datas = {
    'subaction':'test'
    }

    send_message_to_machine(datas, jid)
