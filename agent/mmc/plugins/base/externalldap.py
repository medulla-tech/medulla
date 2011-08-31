# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import ldap
import xmlrpclib
from ConfigParser import NoOptionError

from mmc.site import mmcconfdir
from mmc.plugins.base.ldapconnect import LDAPConnectionConfig, LDAPConnection
from mmc.plugins.base.auth import AuthenticatorConfig, AuthenticatorI, AuthenticationToken
from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI

INI = mmcconfdir + "/plugins/base.ini"

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

    def __init__(self, conffile = INI, name = "externalldap"):
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
                    pass
        except Exception, e:
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
                self.logger.debug("Connecting to %s" % ldapurl)
                self.config.ldapurl = ldapurl
                conn = LDAPConnection(self.config)
                l = conn.l
                if self.config.network_timeout:
                    l.set_option(ldap.OPT_NETWORK_TIMEOUT, self.config.network_timeout)
                if self.config.bindname:
                    l.simple_bind_s(self.config.bindname, self.config.bindpasswd)
                else:
                    l.simple_bind_s()
                connected = True
            except ldap.LDAPError, e:
                self.logger.info("Can't connect to LDAP server %s %s" % (ldapurl, e))
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
        users = l.search_s(self.config.suffix, ldap.SCOPE_SUBTREE, "(&(%s=%s)(%s))" % (self.config.attr, login, self.config.filter))
        for user in users:
            self.logger.debug("Found user dn: %s" % user[0])
            self.logger.debug(str(user))
        # Check that the login string exactly matches LDAP content
        if users and users[0][1][self.config.attr][0] == login:
            ret = users[0]
        else:
            ret = (None, None)
        return ret

    def ldapBind(self, l, userdn, password):
        if isinstance(password, xmlrpclib.Binary):
            password = str(password)
        self.logger.debug("Binding with dn: %s %s" % (userdn, password))
        l.simple_bind_s(userdn, password)


class ExternalLdapProvisionerConfig(ProvisionerConfig):
    """
    Read and store the configuration of ExternalLdapProvisioner objects.
    """

    def readConf(self):
        ProvisionerConfig.readConf(self)
        for attr in ["uid", "givenName", "sn"]:
            option = "ldap_" + attr
            self.__dict__[option] = self.get(self.section, option)
        if self.has_option(self.section, "profile_attr"):
            self.profileAttr = self.get(self.section, "profile_attr")
            if self.has_option(self.section, "profile_group_mapping"):
                self.profileGroupMapping = self.getboolean(self.section, "profile_group_mapping")
            if self.has_option(self.section, "profile_group_prefix"):
                self.profileGroupPrefix = self.get(self.section, "profile_group_prefix")
            PROFILEACL = "profile_acl_"
            for option in self.options(self.section):
                if option.startswith(PROFILEACL):
                    self.profilesAcl[option.replace(PROFILEACL, "").lower()] = self.get(self.section, option)

    def setDefault(self):
        ProvisionerConfig.setDefault(self)
        self.profileAttr = None
        self.profilesAcl = {}
        self.profileGroupMapping = False
        self.profileGroupPrefix = ""


class ExternalLdapProvisioner(ProvisionerI):
    """
    This provisioner creates user accounts thanks to user informations given
    by ExternalLdapAuthenticator objects.
    """

    def __init__(self, conffile = INI, name = "externalldap"):
        ProvisionerI.__init__(self, conffile, name, ExternalLdapProvisionerConfig)

    def doProvisioning(self, authtoken):
        from mmc.plugins.base import ldapUserGroupControl
        self.logger.debug(str(authtoken.getInfos()))
        l = ldapUserGroupControl()
        userentry = authtoken.getInfos()[1]
        uid = userentry[self.config.ldap_uid][0]
        if l.existUser(uid):
            self.logger.debug("User %s already exists, so this user won't be added" % uid)
        else:
            givenName = userentry[self.config.ldap_givenName][0].decode("utf-8")
            sn = userentry[self.config.ldap_sn][0].decode("utf-8")
            l.addUser(uid, authtoken.getPassword(), givenName, sn)
        if self.config.profileAttr and self.config.profilesAcl:
            # Set or update the user right
            try:
                profile = userentry[self.config.profileAttr][0].lower()
            except KeyError:
                self.logger.info("No profile information for user %s in attribute %s" % (uid, self.config.profileAttr))
                profile = ""
            profile = profile.strip()
            try:
                acls = self.config.profilesAcl[profile]
            except KeyError:
                self.logger.info("No ACL defined in configuration file for profile '%s'" % profile)
                self.logger.info("Setting ACL to empty")
                acls = None
            if profile and acls:
                self.logger.info("Setting MMC ACL corresponding to user profile %s: %s" % (profile, str(acls)))
            entry = l.getDetailedUser(uid)
            if not "lmcUserObject" in entry["objectClass"]:
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
                            self.logger.debug('Deleting user %s from group %s' % (uid, groupname))
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
                        self.logger.debug('Adding user %s to group %s' % (uid, groupname))
                        l.addUserToGroup(groupname, uid)

    def validate(self):
        return True
