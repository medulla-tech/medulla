# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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

"""
LDAP connection common classes.
"""

import ldap

class LDAPConnectionConfig:
    """
    Define values needed by the LDAPConnection class.
    """
    
    ldapurl = 'ldap://127.0.0.1:389'
    ldapdebuglevel = 0
    start_tls = False
    ldapverifypeer = ldap.OPT_X_TLS_NEVER
    ciphersuites = 'TLSv1:!NULL'
    cacertdir = None
    cacert = None
    localcert = None
    localkey = None
    network_timeout = None

    def readLDAPConf(self, section):
        """
        Read LDAP configuration from the given section
        """
        # Get LDAP server we are connected to
        try:
            # Host option is deprecated
            self.ldapserver = self.get(section, "host")
        except:
            self.ldapserver = None
        try:
            self.ldapurl = self.get(section, "ldapurl")
        except:
            self.ldapurl = None
        if not self.ldapurl and self.ldapserver:
            self.ldapurl = 'ldap://' + self.ldapserver
        try:
            self.network_timeout = self.getint(section, "network_timeout")
        except:
            pass
        # Get SSL/TLS parameters
        try:
            self.start_tls = self.getboolean(section, 'start_tls')
        except:
            pass
        try:
            self.ldapverifypeer = self.get(section, 'ldapverifypeer')
        except:
            pass
        try:
            self.cacert = self.get(section, 'cacert')
        except:
            pass
        try:
            self.cacertdir = self.get(section, 'cacertdir')
        except:
            pass
        try:
            self.localcert = self.get(section, 'localcert')
        except:
            pass
        try:
            self.localkey = self.get(section, 'localkey')
        except:
            pass
        try:
            self.ciphersuites = self.get(section, 'ciphersuites')
        except:
            pass
        # Get LDAP operations debug level
        try:
            self.ldapdebuglevel = self.getint(section, 'ldapdebuglevel')
        except:
            pass

class LDAPConnection:

    def __init__(self, config):
        """
        Set up LDAP connection according to the given configuration.
        
        @param config: LDAP connection configuration
        @type config: LDAPConnectionConfigI
        """
        ldap.set_option(ldap.OPT_DEBUG_LEVEL, config.ldapdebuglevel)
        self.l = ldap.initialize(config.ldapurl)
        self.l.protocol_version = ldap.VERSION3
        if config.network_timeout != None:
            self._ldapSetOption(self.l, ldap.OPT_NETWORK_TIMEOUT, config.network_timeout)
        if config.start_tls or config.ldapurl.startswith('ldaps://'):
            # Set SSL/TLS options
            verifypeer = ldap.OPT_X_TLS_NEVER
            if config.ldapverifypeer == 'demand':
                verifypeer = ldap.OPT_X_TLS_DEMAND
            self._ldapSetOption(self.l, ldap.OPT_X_TLS_REQUIRE_CERT, verifypeer)
            self._ldapSetOption(self.l, ldap.OPT_X_TLS_CIPHER_SUITE, config.ciphersuites)
            if config.cacertdir:
                self._ldapSetOption(self.l, ldap.OPT_X_TLS_CACERTDIR, config.cacertdir)
            if config.cacert:
                self._ldapSetOption(self.l, ldap.OPT_X_TLS_CACERTFILE, config.cacert)
            if config.localcert:
                self._ldapSetOption(self.l, ldap.OPT_X_TLS_CERTFILE, config.localcert)
            if config.localkey:
                self._ldapSetOption(self.l, ldap.OPT_X_TLS_KEYFILE, config.localkey)

        if config.start_tls:
            self.l.start_tls_s()
        
    def _ldapSetOption(self, conn, parameter, value):
        """
        Set LDAP option to a LDAP connection.
        Fallback to global ldap.set_option if there is an error. Errors can
        happen according to the current OpenLDAP client libs. 2.4 client libs
        allow more operations.
        """
        try:
            conn.set_option(parameter, value)
        except ldap.LDAPError:
            ldap.set_option(parameter, value)

    def get(self):
        return self.l
