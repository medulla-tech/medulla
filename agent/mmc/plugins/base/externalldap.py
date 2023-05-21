# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import imp
import ldap
import xmlrpc.client
from configparser import NoOptionError

from mmc.site import mmcconfdir
from mmc.plugins.base.ldapconnect import LDAPConnectionConfig, LDAPConnection
from mmc.plugins.base.auth import (
    AuthenticatorConfig,
    AuthenticatorI,
    AuthenticationToken,
)
from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI

INI = f"{mmcconfdir}/plugins/base.ini"


class ExternalLdapAuthenticatorConfig(AuthenticatorConfig, LDAPConnectionConfig):
    """
    Read and store the configuration of ExternalLdapAuthenticator objects.
    """

    def readConf(self):
        AuthenticatorConfig.readConf(self)
        for option in ["suffix", "attr"]:
            self.__dict__[option] = self.get(self.section, option)
        try:
            self.__dict__["bindname"] = self.getdn(self.section, "bindname")
        except NoOptionError:
            pass
        try:
            self.__dict__["bindpasswd"] = self.getpassword(self.section, "bindpasswd")
        except NoOptionError:
            pass
        self.ldapurls = self.get(self.section, "ldapurl").split()
        try:
            self.filter = self.get(self.section, "filter")
        except NoOptionError:
            pass

    def setDefault(self):
        AuthenticatorConfig.setDefault(self)
        self.filter = "objectClass=*"
        self.bindname = None
        self.bindpasswd = None


class ExternalLdapAuthenticator(AuthenticatorI):
    """
    This authenticator connects to a LDAP server to authenticate users.
    """

    def __init__(self, conffile=INI, name="externalldap"):
        AuthenticatorI.__init__(self, conffile, name, ExternalLdapAuthenticatorConfig)

    def validate(self):
        ret = False
        if self.config:
            self.connect()
            ret = True
        return ret

    def authenticate(self, user, password):
        ret = False
        userdn = None
        userentry = None
        try:
            l = self.connect()
            userdn, userentry = self.searchUser(l, user)
            if userdn:
                try:
                    self.ldapBind(l, userdn, password)
                    ret = True
                except ldap.INVALID_CREDENTIALS:
                    self.logger.debug("Invalid credentials")
        except Exception as e:
            self.logger.exception(e)
            ret = False
        return AuthenticationToken(ret, user, password, (userdn, userentry))

    def connect(self):
        """
        @return: a LDAPobject connected to the LDAP
        @rtype: LDAPObject
        """
        connected = False
        for ldapurl in self.config.ldapurls:
            try:
                self.logger.debug(f"Connecting to {ldapurl}")
                self.config.ldapurl = ldapurl
                conn = LDAPConnection(self.config)
                l = conn.l
                l.set_option(ldap.OPT_REFERRALS, ldap.OPT_OFF)
                if self.config.network_timeout:
                    l.set_option(ldap.OPT_NETWORK_TIMEOUT, self.config.network_timeout)
                if self.config.bindname:
                    l.simple_bind_s(self.config.bindname, self.config.bindpasswd)
                else:
                    l.simple_bind_s()
                connected = True
            except ldap.LDAPError as e:
                self.logger.info(f"Can't connect to LDAP server {ldapurl} {e}")
            if connected:
                # Exit loop, because we found a LDAP server to connect to
                break
        if not connected:
            raise Exception("Can't find an external LDAP server to connect to")
        return l

    def searchUser(self, l, login):
        """
        Search the user dn into the LDAP

        @return: a couple (user DN, user entry)
        """
        users = l.search_s(
            self.config.suffix,
            ldap.SCOPE_SUBTREE,
            f"(&({self.config.attr}={login})({self.config.filter}))",
        )
        for user in users:
            self.logger.debug(f"Found user dn: {user[0]}")
            self.logger.debug(str(user))
        return (
            users[0]
            if users and users[0][1][self.config.attr][0] == login
            else (None, None)
        )

    def ldapBind(self, l, userdn, password):
        if isinstance(password, xmlrpc.client.Binary):
            password = str(password)
        self.logger.debug(f"Binding with dn: {userdn} {password}")
        l.simple_bind_s(userdn, password)


class ExternalLdapProvisionerConfig(ProvisionerConfig):
    """
    Read and store the configuration of ExternalLdapProvisioner objects.
    """

    def readConf(self):
        ProvisionerConfig.readConf(self)
        for attr in ["uid", "givenName", "sn"]:
            option = f"ldap_{attr}"
            self.__dict__[option] = self.get(self.section, option)
        if self.has_option(self.section, "profile_attr"):
            self.profileAttr = self.get(self.section, "profile_attr")
            if self.has_option(self.section, "profile_group_mapping"):
                self.profileGroupMapping = self.getboolean(
                    self.section, "profile_group_mapping"
                )
            if self.has_option(self.section, "profile_group_prefix"):
                self.profileGroupPrefix = self.get(self.section, "profile_group_prefix")
            PROFILEACL = "profile_acl_"
            for option in self.options(self.section):
                if option.startswith(PROFILEACL):
                    self.profilesAcl[option.replace(PROFILEACL, "").lower()] = self.get(
                        self.section, option
                    )

            PROFILEENTITY = "profile_entity_"
            for option in self.options(self.section):
                if option.startswith(PROFILEENTITY):
                    self.profilesEntity[
                        option.replace(PROFILEENTITY, "").lower()
                    ] = self.get(self.section, option)

    def setDefault(self):
        ProvisionerConfig.setDefault(self)
        self.profileAttr = None
        self.profilesAcl = {}
        self.profileGroupMapping = False
        self.profileGroupPrefix = ""
        self.profilesEntity = {}


class ExternalLdapProvisioner(ProvisionerI):
    """
    This provisioner creates user accounts thanks to user informations given
    by ExternalLdapAuthenticator objects.
    """

    def __init__(self, conffile=INI, name="externalldap"):
        ProvisionerI.__init__(self, conffile, name, ExternalLdapProvisionerConfig)

    def doProvisioning(self, authtoken):
        from mmc.plugins.base import ldapUserGroupControl

        self.logger.debug(str(authtoken.getInfos()))
        l = ldapUserGroupControl()
        userentry = authtoken.getInfos()[1]
        uid = userentry[self.config.ldap_uid][0]
        if l.existUser(uid):
            self.logger.debug(f"User {uid} already exists, so this user won't be added")
        else:
            givenName = userentry[self.config.ldap_givenName][0].decode("utf-8")
            sn = userentry[self.config.ldap_sn][0].decode("utf-8")
            l.addUser(uid, authtoken.getPassword(), givenName, sn)
        if self.config.profileAttr and self.config.profilesAcl:
            # Set or update the user right
            try:
                profile = userentry[self.config.profileAttr][0].lower()
            except KeyError:
                self.logger.info(
                    f"No profile information for user {uid} in attribute {self.config.profileAttr}"
                )
                profile = ""
            profile = profile.strip()

            try:
                entities = self.config.profilesEntity[profile].split()
                self.logger.info(f"*******ENTITE '{entities}' ")
            except KeyError:
                if "default" in self.config.profilesEntity:
                    entities = self.config.profilesEntity["default"].split()
                    self.logger.info("Set the default profile to user.")
                    profile = "default"
                else:
                    self.logger.info(
                        f"No entity defined in configuration file for profile '{profile}'"
                    )
                    self.logger.info("Setting user's entity to empty")
                    entities = []
            if profile and entities:
                tmp = []
                for entity in entities:
                    if entity.startswith("%") and entity.endswith("%"):
                        attr = entity.strip("%")
                        if attr in userentry:
                            tmp.extend(userentry[attr])
                        else:
                            self.logger.info(f"The user '{uid}' doesn't have an attribute '{attr}'")

                    elif entity.startswith("plugin:"):
                        plugin = entity.replace("plugin:", "")
                        searchpath = os.path.join(
                            os.path.dirname(__file__), "provisioning_plugins"
                        )
                        try:
                            f, p, d = imp.find_module(plugin, [searchpath])
                            mod = imp.load_module(plugin, f, p, d)
                            klass = mod.PluginEntities
                            found = klass().get(authtoken)
                            if found:
                                self.logger.info(f"Plugin '{plugin}' found these entities: {found}")
                            else:
                                self.logger.info(f"Plugin '{plugin}' found no matching entity")
                            tmp.extend(found)
                        except ImportError:
                            self.logger.error(f"The plugin '{plugin}' can't be imported")
                        except Exception as e:
                            self.logger.error(f"Error while using the plugin '{plugin}'")
                            self.logger.exception(e)

                    else:
                        tmp.append(entity)
                entities = tmp[:]
                self.logger.info(
                    f"****Setting user '{uid}' entities corresponding to user profile '{profile}': {str(entities)}"
                )
                from pulse2.database.inventory import Inventory

                Inventory().setUserEntities(uid, entities)

            try:
                acls = self.config.profilesAcl[profile]
            except KeyError:
                self.logger.info(
                    f"No ACL defined in configuration file for profile '{profile}'"
                )
                self.logger.info("Setting ACL to empty")
                acls = None
            if profile and acls:
                self.logger.info(
                    f"Setting MMC ACL corresponding to user profile {profile}: {str(acls)}"
                )
            entry = l.getDetailedUser(uid)
            if "lmcUserObject" not in entry["objectClass"]:
                entry["objectClass"].append("lmcUserObject")
                l.changeUserAttributes(uid, "objectClass", entry["objectClass"])
            l.changeUserAttributes(uid, "lmcAcl", acls)
            if self.config.profileGroupMapping:
                # Set user group membership according to mapping
                for prof in self.config.profilesAcl:
                    groupname = self.config.profileGroupPrefix + prof
                    if prof != profile:
                        # Delete the user from a group not belonging to her/his
                        # profile
                        try:
                            l.delUserFromGroup(groupname, uid)
                            self.logger.debug(f"Deleting user {uid} from group {groupname}")
                        except ldap.NO_SUCH_OBJECT:
                            # The group does not exist
                            pass
                    else:
                        # Add the user to this group
                        try:
                            l.addGroup(groupname)
                        except ldap.ALREADY_EXISTS:
                            # This group already exists
                            pass
                        self.logger.debug(f"Adding user {uid} to group {groupname}")
                        l.addUserToGroup(groupname, uid)

    def validate(self):
        return True
