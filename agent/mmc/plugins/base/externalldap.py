# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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
import logging
import ConfigParser
import xmlrpclib

from mmc.plugins.base.auth import *
from mmc.plugins.base.provisioning import *

INI = "/etc/mmc/plugins/base.ini"

class ExternalLdapAuthenticatorConfig(AuthenticatorConfig):
    """
    Read and store the configuration of ExternalLdapAuthenticator objects.
    """
    
    def readConf(self):
        AuthenticatorConfig.readConf(self)
        for option in ["suffix", "bindname", "bindpasswd", "attr"]:
            self.__dict__[option] = self.get(self.section, option)
        self.ldapurls = self.get(self.section, "ldapurl").split()
        try:
            self.filter = self.get(self.section, "filter")
        except NoOptionError:
            pass

    def setDefault(self):
        AuthenticatorConfig.setDefault(self)
        self.filter = "objectClass=*"
        

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
                l = ldap.initialize(ldapurl)
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
            raise "Can't find a external LDAP server to connect to"
        return l

    def searchUser(self, l, user):
        """
        Search the user dn into he LDAP

        @return: a couple (user DN, user entry)
        """
        users = l.search_s(self.config.suffix, ldap.SCOPE_SUBTREE, "(&(%s=%s)(%s))" % (self.config.attr, user, self.config.filter))
        for user in users:
            self.logger.debug("Found user dn: %s" % user[0])
            self.logger.debug(str(user))
        if users:
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

    def validate(self):
        return True
